from datetime import datetime
from seedboxsync.__version__ import __api_path_version__ as api_path_version
from seedboxsync.core.database.models import Log

API_PATH = f"/api/{api_path_version}"


def test_get_logs_date_filter_includes_entire_end_date(new_database_app):
    app, _ = new_database_app
    log_timestamps = [
        datetime(2099, 6, 2, 23, 59, 59),
        datetime(2099, 6, 3, 0, 0, 0),
        datetime(2099, 6, 3, 23, 59, 59),
        datetime(2099, 6, 4, 0, 0, 0),
    ]

    with app.app_context():
        for timestamp in log_timestamps:
            Log.create(
                level_name="INFO",
                logger_name="test",
                message=timestamp.isoformat(),
                timestamp=timestamp,
            )

    app.extensions["flaskdb"].database.close()
    response = app.test_client().get(f"{API_PATH}/logs?start_date=2099-06-03&end_date=2099-06-03")

    assert response.status_code == 200, response.get_data(as_text=True)
    assert response.json["data_total"] == 2
    assert {log["message"] for log in response.json["data"]} == {
        "2099-06-03T00:00:00",
        "2099-06-03T23:59:59",
    }
