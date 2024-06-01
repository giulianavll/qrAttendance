from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from .models import Student, Attendance
from django.http import JsonResponse
from datetime import datetime, timedelta
from django.db.models import OuterRef, Subquery, Exists
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import csv


def index(request):
    if request.user.is_authenticated:
        return render(request, "core/index.html")
    else:
        return redirect("login_view")


def attendance(request):
    try:
        key = request.POST.get("code", None)
        if request.method == "POST" and request.user.is_authenticated and key:
            # student = Student.objects.get(key=key)
            student, created = Student.objects.get_or_create(
                key=key, defaults={"key": key, "name": key, "group": "undefined", "code": "undefined"}
            )
            user = request.user
            register = Attendance(student=student, created_by=user)
            register.save()
            return JsonResponse({"isOk": True, "name": student.name}, status=200)

        return JsonResponse({"isOk": False, "msg": "bad request"}, status=204)
    except Student.DoesNotExist:
        return JsonResponse({"isOk": False, "msg": "Student not found"}, status=200)
    except Exception as e:
        print(e)
        return JsonResponse({"isOk": False, "msg": "bad request"}, status=204)


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("index")
        else:
            return render(request, "core/login.html", context={"error": True})
    else:
        if request.user.is_authenticated:
            return redirect("index")

        return render(request, "core/login.html")


def logout_view(request):
    logout(request)
    return redirect("login_view")


def retrieve_attendance(begin, end, only_unchecked):
    # to UTC plus 5 hours
    min_dt = begin + timedelta(hours=5)
    max_dt = end + timedelta(hours=5)

    contCheck = 0
    if only_unchecked:
        list_checked = Attendance.objects.filter(created_on__range=(min_dt, max_dt)).values("student")
        students = Student.objects.exclude(pk__in=list_checked).order_by("name").values()

    else:
        subquery = Attendance.objects.filter(student=OuterRef("pk"), created_on__range=(min_dt, max_dt))
        students = (
            Student.objects.annotate(check=Exists(subquery), timestamp=Subquery(subquery.values("created_on")))
            .order_by("name")
            .values()
        )

        # to GMT -5
        for student in students:
            if student["timestamp"]:
                contCheck = contCheck + 1
                student["timestamp"] = student["timestamp"] - timedelta(hours=5)

    return students, contCheck


@login_required
def report(request):
    if request.method == "GET":
        return render(request, "core/report.html", context={"begin": "", "end": ""})
    elif request.method == "POST":
        begin = request.POST.get("begin_time", None)
        end = request.POST.get("end_time", None)
        format_csv = request.POST.get("format_csv", None)
        only_unchecked = request.POST.get("only_unchecked", None)
        only_unchecked = True if only_unchecked else False

        if begin and end:
            str_format = "%Y-%m-%dT%H:%M"
            str_format_view = "%d-%m %H:%M"
            begin_object = datetime.strptime(begin, str_format)
            end_object = datetime.strptime(end, str_format)

            students, cont_check = retrieve_attendance(begin_object, end_object, only_unchecked)
            cont_total = len(students)

            if format_csv == "":
                range_str = f"from_{begin_object.strftime(str_format_view)}_to_{end_object.strftime(str_format_view)}"
                filename = f"report_{range_str}.csv"
                response = HttpResponse(
                    content_type="text/csv",
                    headers={"Content-Disposition": f'attachment; filename="{filename}"'},
                )
                writer = csv.writer(response)
                writer.writerow(["DNI", "Nombres", "Asistencia", range_str])
                if only_unchecked:
                    for student in students:
                        writer.writerow([student["key"], student["name"], "no"])
                else:
                    for student in students:
                        check = "si" if student["check"] else "no"
                        timestamp = student["timestamp"].strftime(str_format_view) if student["timestamp"] else ""
                        writer.writerow([student["key"], student["name"], check, timestamp])
                return response

            else:
                return render(
                    request,
                    "core/report.html",
                    context={
                        "begin": begin_object.strftime(str_format),
                        "end": end_object.strftime(str_format),
                        "table": students,
                        "contCheck": cont_check,
                        "contTotal": cont_total,
                        "only_unchecked": only_unchecked,
                    },
                )

        return render(request, "core/report.html", context={"begin": "", "end": ""})
    else:
        return redirect("login_view")
