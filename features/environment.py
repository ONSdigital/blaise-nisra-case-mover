from blaise_nisra_case_mover import app


def before_feature(context, feature):
    app.testing = True
    context.client = app.test_client()