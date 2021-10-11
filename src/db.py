import pymysql
from pymysql import cursors
from flask import _app_ctx_stack, current_app


class MySQL(object):

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Initialize the `app` for use with this
        :class:`~flask_pymysql.MySQL` class.
        This is called automatically if `app` is passed to
        :meth:`~MySQL.__init__`.
        :param flask.Flask app: the application to configure for use with
            this :class:`~flask_pymysql.MySQL` class.
        """

        if hasattr(app, 'teardown_appcontext'):
            app.teardown_appcontext(self.teardown)

    @property
    def connect(self):
        if current_app.config['pymysql_kwargs']:
            kwargs = current_app.config['pymysql_kwargs']
            if 'cursorclass' in kwargs.keys():
                kwargs['cursorclass'] = getattr(cursors, kwargs['cursorclass'])
        else:
            kwargs = dict()

        return pymysql.connect(**kwargs)

    @property
    def connection(self):
        """Attempts to connect to the MySQL server.
        :return: Bound MySQL connection object if successful or ``None`` if
            unsuccessful.
        """

        ctx = _app_ctx_stack.top
        if ctx is not None:
            if not hasattr(ctx, 'mysql_db'):
                ctx.mysql_db = self.connect
            return ctx.mysql_db

    def teardown(self, exception):
        ctx = _app_ctx_stack.top
        if hasattr(ctx, 'mysql_db'):
            ctx.mysql_db.close()
