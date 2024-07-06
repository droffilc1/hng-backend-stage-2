#!/usr/bin/env python3
"""Home."""
from flask import Blueprint, jsonify

home_bp = Blueprint('home', __name__)


@home_bp.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Hello World"})
