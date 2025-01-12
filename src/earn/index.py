import os
import sys
import pandas as pd
from json import load
from flask import Blueprint, render_template
sys.path.append("..")
from utils import current_path

earn = Blueprint("earn", __name__, template_folder="templates", url_prefix="/earn")

@earn.route("/<currency>")
def hello(currency):
    output_dir = os.path.join(current_path(), "datas", "results")
    output_list = []
    for each_obj in os.listdir(output_dir):
        file_path = os.path.join(output_dir, each_obj)
        if not os.path.isfile(file_path):
            continue
        if not each_obj.startswith(f"{currency}_earn"):
            continue
        with open(file_path, "r") as fr:
            each_dict = load(fr)
        output_list.append(each_dict)
    table = pd.DataFrame(output_list).sort_values(by="update_time", ascending=False).to_html(header=True, index=False, classes=currency)
    return render_template("index.html", title=currency, table=table)
