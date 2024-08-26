# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from app.home import blueprint
from flask import render_template, redirect, url_for, request
from flask_login import login_required, current_user
from app import login_manager
from jinja2 import TemplateNotFound
from app.base.models import Task
import json
from app import db

@blueprint.route('/index')
@login_required
def index():

    return render_template('index.html', segment='index')

@blueprint.route('/<template>')
@login_required
def route_template(template):

    try:

        if not template.endswith( '.html' ):
            template += '.html'

        # Detect the current page
        segment = get_segment( request )

        # Serve the file (if exists) from app/templates/FILE.html
        return render_template( template, segment=segment )

    except TemplateNotFound:
        return render_template('page-404.html'), 404
    
    except:
        return render_template('page-500.html'), 500

# Helper - Extract current page name from request 
def get_segment( request ): 

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment    

    except:
        return None  

@blueprint.route("/initserver/",methods=["POST","GET"])
def init_server():
    task_dict = {}
    if request.method=="POST":
        gpu = request.form.get("gpu")
        num_of_clients = request.form.get("num_of_clients")
        cfraction = request.form.get("cfraction")
        epoch = request.form.get("epoch")
        batchsize = request.form.get("batchsize")
        modelname = request.form.get("modelname")
        learning_rate = request.form.get("learning_rate")
        val_freq = request.form.get("val_freq")
        save_freq = request.form.get("save_freq")
        num_comm = request.form.get("num_comm")
        save_path = request.form.get("save_path")
        iid = request.form.get("iid")

        task = Task()

        task.gpu = gpu
        task.num_of_clients = num_of_clients
        task.cfraction = cfraction
        task.epoch = epoch
        task.batchsize = batchsize
        task.modelname = modelname
        task.learning_rate = learning_rate
        task.val_freq = val_freq
        task.save_freq = save_freq
        task.save_path = save_path
        task.num_comm = num_comm
        task.iid = iid

        task_dict = {
            "gpu": int(gpu),
            "num_of_clients": int(num_of_clients),
            "cfraction": float(cfraction),
            "epoch": int(epoch),
            "batchsize": int(batchsize),
            "modelname": modelname,
            "learning_rate": float(learning_rate),
            "val_freq": int(val_freq),
            "save_freq": int(save_freq),
            "num_comm": int(num_comm), 
            "save_path": save_path, 
            "iid": int(iid)
        }
        if task.save():
            with open("initparam.json","w+") as f:
                json.dump(task_dict,f)
                f.close()
            return render_template("submit_success.html")
        else:
            return render_template("submit_fail.html")

    elif request.method=="GET":
        task = Task.query.order_by(Task.id.desc()).first()
        task_dict = {
            "gpu": task.gpu,
            "num_of_clients": task.num_of_clients,
            "cfraction": task.cfraction,
            "epoch": task.epoch,
            "batchsize": task.batchsize,
            "modelname": task.modelname,
            "learning_rate": task.learning_rate,
            "val_freq": task.val_freq,
            "save_freq": task.save_freq,
            "num_comm": task.num_comm, 
            "save_path": task.save_path, 
            "iid": task.iid
        }
        task_dict = json.dumps(task_dict)

        return task_dict

