"""Public section, including homepage and signup."""

from urllib.parse import urlparse

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import login_required, login_user, logout_user

from anime.extensions import login_manager
from anime.public.forms import LoginForm
from anime.user.forms import RegisterForm
from anime.user.models import User
from anime.utils import flash_errors

blueprint = Blueprint("public", __name__, static_folder="../static")


def is_safe_redirect_url(target):
    """Return True if the redirect target is a safe local URL."""
    if not target:
        return False
    # Normalize backslashes, which some browsers accept as path separators.
    target = target.replace("\\", "/")
    parsed = urlparse(target)
    # Disallow any URL that specifies a scheme or network location.
    if parsed.scheme or parsed.netloc:
        return False
    # Only allow relative paths within this application.
    return target.startswith("/")


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID."""
    return User.get_by_id(int(user_id))


@blueprint.route("/", methods=["GET", "POST"])
def home():
    """Home page."""
    form = LoginForm(request.form)
    current_app.logger.info("Hello from the home page!")
    # Handle logging in
    if request.method == "POST":
        if form.validate_on_submit():
            login_user(form.user)
            flash("You are logged in.", "success")
            next_url = request.args.get("next")
            if next_url and is_safe_redirect_url(next_url):
                redirect_url = next_url
            else:
                redirect_url = url_for("user.members")
            return redirect(redirect_url)
        else:
            flash_errors(form)
    return render_template("public/home.html", form=form)


@blueprint.route("/logout/")
@login_required
def logout():
    """Logout."""
    logout_user()
    flash("You are logged out.", "info")
    return redirect(url_for("public.home"))


@blueprint.route("/register/", methods=["GET", "POST"])
def register():
    """Register new user."""
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        User.create(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
            active=True,
        )
        flash("Thank you for registering. You can now log in.", "success")
        return redirect(url_for("public.home"))
    else:
        flash_errors(form)
    return render_template("public/register.html", form=form)


@blueprint.route("/about/")
def about():
    """About page."""
    form = LoginForm(request.form)
    return render_template("public/about.html", form=form)
