from flask import render_template
from app import db
from app.errors import bp

@bp.app_errorhandler(404)
def not_found_error(error):
    ''' return the rendered 404 template html and the error code(int) '''
    return render_template('errors/404.html'), 404

@bp.app_errorhandler(500)
def internal_server_error(error):
    ''' return the rendered 500 template html and the error code(int) '''
    db.session.rollbak()
    return render_template('errors/500.html'), 500

