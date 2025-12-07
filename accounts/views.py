from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.views.decorators.csrf import csrf_exempt
import xml.etree.ElementTree as ET, uuid
from .models import UserProfile
from django.test import RequestFactory
from django.urls import resolve

# --------------------  USER DATABASE --------------------
USERS = {
    "student01": {"password": "123", "role": "student"},
    "tutor01": {"password": "123", "role": "tutor"},
    # "admin01": {"password": "123", "role": "admin"},
    "office01": {"password": "123", "role": "office"},
}

# --------------------  CAS CONFIG --------------------
CAS_SERVER_URL = "http://127.0.0.1:8000/cas"
SERVICE_URL = "http://127.0.0.1:8000/sso/callback/"

# -------------------- MAIN LOGIN PAGE --------------------
def login_page(request):
    return render(request, "accounts/login.html")

# -------------------- REDIRECT TO CAS LOGIN --------------------
def sso_login(request):
    sso_login_url = f"{CAS_SERVER_URL}/login?service={SERVICE_URL}"
    return redirect(sso_login_url)

# -------------------- HANDLE CAS CALLBACK --------------------
def sso_callback(request):
    token = request.GET.get("token")
    if not token:
        return HttpResponse("No token provided.")

    # Instead of requests.get(), call cas_validate directly
    factory = RequestFactory()
    fake_request = factory.get('/cas/serviceValidate', {
        'token': token,
        'service': SERVICE_URL
    })
    fake_request.session = request.session  # share session

    # Call the internal Django view directly
    view_func = resolve('/cas/serviceValidate').func
    response = view_func(fake_request)

    # Parse XML result
    ns = {'cas': 'http://www.yale.edu/tp/cas'}
    root = ET.fromstring(response.content)
    success = root.find('cas:authenticationSuccess', ns)
    if success is None:
        return HttpResponse("Invalid or expired token.")

    username = success.find('cas:user', ns).text
    role_elem = success.find('cas:attributes/cas:role', ns)
    role = role_elem.text if role_elem is not None else "student"
    email = f"{username}@hcmut.edu.vn"

    # Create or update user
    user, _ = User.objects.get_or_create(username=username, defaults={'email': email})
    profile, _ = UserProfile.objects.get_or_create(user=user, defaults={'role': role})
    if profile.role != role:
        profile.role = role
        profile.save()

    login(request, user)

    # Redirect by role
    if role == "student":
        return redirect("students:student_dashboard")
    elif role == "tutor":
        return redirect("tutors:tutor_dashboard")
    # elif role == "admin":
    #     return redirect("admin_dashboard")
    elif role == "office":
        return redirect("office_dashboard")
    else:
        return redirect("/")

# --------------------  CAS LOGIN PAGE --------------------
@csrf_exempt
def cas_login(request):
    service = request.GET.get("service", SERVICE_URL)
    context = {}

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user_info = USERS.get(username)

        if user_info and user_info["password"] == password:
            token = f"ST-{uuid.uuid4()}"
            request.session["token_user"] = username
            request.session["token_role"] = user_info["role"]
            request.session["token_value"] = token
            return redirect(f"{service}?token={token}")
        else:
            context["error"] = "Invalid username or password"

    return render(request, "accounts/hcmut_sso.html", context)

# --------------------  CAS VALIDATION ENDPOINT --------------------
def cas_validate(request):
    token = request.GET.get("token")
    stored_token = request.session.get("token_value")
    username = request.session.get("token_user")
    role = request.session.get("token_role", "student")

    if token == stored_token and username:
        return HttpResponse(f"""
            <cas:serviceResponse xmlns:cas="http://www.yale.edu/tp/cas">
              <cas:authenticationSuccess>
                <cas:user>{username}</cas:user>
                <cas:attributes>
                    <cas:role>{role}</cas:role>
                </cas:attributes>
              </cas:authenticationSuccess>
            </cas:serviceResponse>
        """, content_type="text/xml")
    else:
        return HttpResponse("""
            <cas:serviceResponse xmlns:cas="http://www.yale.edu/tp/cas">
              <cas:authenticationFailure code="INVALID_TOKEN">
                Token not recognized
              </cas:authenticationFailure>
            </cas:serviceResponse>
        """, content_type="text/xml")
