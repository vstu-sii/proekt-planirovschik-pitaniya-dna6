import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


def demo_days(count: int, max_cook_time_min: int = 240) -> list[dict]:
    meals = [
        {
            "name": "Овсянка с яблоком",
            "meal_type": "breakfast",
            "cook_time_min": 10,
            "ingredients": [
                {"name": "Овсяные хлопья", "amount_g": 70},
                {"name": "Яблоко", "amount_g": 150},
                {"name": "Молоко", "amount_g": 150},
            ],
        },
        {
            "name": "Гречка с курицей",
            "meal_type": "lunch",
            "cook_time_min": 25,
            "ingredients": [
                {"name": "Гречка", "amount_g": 90},
                {"name": "Куриная грудка", "amount_g": 160},
                {"name": "Морковь", "amount_g": 80},
            ],
        },
        {
            "name": "Тёплый салат с фасолью",
            "meal_type": "dinner",
            "cook_time_min": 20,
            "ingredients": [
                {"name": "Фасоль консервированная", "amount_g": 180},
                {"name": "Помидор", "amount_g": 150},
                {"name": "Яйцо", "amount_g": 60},
            ],
        },
    ]
    adapted = [
        {**meal, "cook_time_min": min(meal["cook_time_min"], max_cook_time_min)}
        for meal in meals
    ]
    return [{"day": day, "meals": adapted} for day in range(1, count + 1)]


class Handler(BaseHTTPRequestHandler):
    def send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            self.send_json(200, {"status": "ok", "provider": "llm-mock"})
        else:
            self.send_json(404, {"error": "not_found"})

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/v1/generate":
            self.send_json(404, {"error": "not_found"})
            return
        length = int(self.headers.get("Content-Length", "0"))
        request = json.loads(self.rfile.read(length) or b"{}")
        self.send_json(
            200,
            {
                "days": demo_days(
                    int(request.get("days", 1)),
                    int(request.get("max_cook_time_min", 240)),
                ),
                "retry_count": 0,
            },
        )

    def log_message(self, format: str, *args: object) -> None:
        return


ThreadingHTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
