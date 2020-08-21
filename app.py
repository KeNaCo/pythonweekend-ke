from random import randint
from time import sleep
from uuid import uuid4, UUID

from flask import Blueprint, Flask, request, jsonify, current_app

provider1_bp = Blueprint('provider1_bp', __name__, url_prefix='/v1')


@provider1_bp.route('/charge', methods=['POST'])
def charge_payment():
    payment = request.json
    invalid_conditions = (
        lambda payment: 'amount' not in payment,
        lambda payment: 'currency' not in payment,
        lambda payment: len(payment['currency']) != 3,
    )
    if any(condition(payment) for condition in invalid_conditions):
        return jsonify({}), 400
    return jsonify({'transaction_id': uuid4()}), 200


provider2_bp = Blueprint('provider2_bp', __name__, url_prefix='/v2')


@provider2_bp.route('/authorize', methods=['POST'])
def authorize_payment():
    payment = request.json
    invalid_conditions = (
        lambda payment: 'merchant' not in payment,
        lambda payment: 'amount_of_money' not in payment,
        lambda payment: 'amount' not in payment['amount_of_money'],
        lambda payment: 'currency' not in payment['amount_of_money'],
        lambda payment: not isinstance(payment['amount_of_money']['amount'], int)
    )
    if any(condition(payment) for condition in invalid_conditions):
        return jsonify({}), 400
    return jsonify({'payment_reference': uuid4()}), 200


@provider2_bp.route('/capture', methods=['POST'])
def capture_payment():
    payment = request.json
    if 'payment_reference' not in payment:
        return jsonify({'reason': 'Missing payment reference'}), 400
    try:
        UUID(payment['payment_reference'])
    except ValueError:
        return jsonify({'reason': 'Not valid UUID reference.'}), 400
    return jsonify({}), 200


provider3_bp = Blueprint('provider3_bp', __name__, url_prefix='/v3')


@provider3_bp.route('/authorize', methods=['POST'])
def v3_authorize_payment():
    # slowing down request
    sleep(randint(*current_app.config['SLOW_PROVIDER_RESPONSES']))

    payment = request.json
    if 'amount' not in payment:
        return jsonify({'status': 400, 'error': 1}), 200
    if 'currency' not in payment:
        return jsonify({'status': 400, 'error': 2}), 200
    try:
        int(payment['amount'])
    except ValueError:
        return jsonify({'status': 400, 'error': 3}), 200
    if len(payment['currency']) != 3:
        return jsonify({'status': 400, 'error': 4}), 200
    return jsonify({'status': 200, 'payment_id': uuid4()}), 200


@provider3_bp.route('/capture/<payment_id>', methods=['POST'])
def v3_capture_payment(payment_id):
    # slowing down request
    sleep(randint(*current_app.config['SLOW_PROVIDER_RESPONSES']))

    try:
        UUID(payment_id)
    except ValueError:
        return jsonify({'status': 400, 'description': 'Invalid payment ID'}), 200

    return jsonify({'status': 200}), 200


system_bp = Blueprint('system_bp', __name__)


@system_bp.route('/ping')
def ping():
    return 'pong', 200


app = Flask(__name__)
app.config.from_pyfile('app.cfg')  # default
app.config.from_envvar('APP_CONFIG', silent=True)  # override
app.register_blueprint(system_bp)
app.register_blueprint(provider1_bp)
app.register_blueprint(provider2_bp)
app.register_blueprint(provider3_bp)
