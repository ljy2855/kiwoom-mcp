"""Entrypoint for running the Kiwoom dashboard web server."""

import uvicorn


def main() -> None:
    """Run the dashboard app on a dedicated local port."""

    uvicorn.run("src.dashboard:app", host="127.0.0.1", port=8001, reload=False)


if __name__ == "__main__":
    main()
