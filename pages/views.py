from flask import Blueprint, render_template, request

pages = Blueprint("pages", __name__, template_folder="templates")


@pages.route("/ua/")
def ua():
    remote_addr = request.remote_addr
    headers = {k: v for k, v in request.headers.items()}
    return render_template("ua.html", **{
            "remote_addr": remote_addr,
            "headers": headers
        })

