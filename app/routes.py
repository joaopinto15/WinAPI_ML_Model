from flask import Blueprint, request, jsonify
from .model_handler import predict, train_buffer, train_start

main_bp = Blueprint('main', __name__)

@main_bp.route('/predict', methods=['POST'])
def predictRequest():
    return predict(request)

@main_bp.route('/train-buffer', methods=['POST'])
def buffer():
    return train_buffer(request)

@main_bp.route('/train-start', methods=['POST'])
def train():
    return train_start()