def setup_routes(app, handler, project_root):
    router = app.router
    h = handler
    router.add_get("/submit", h.test_submit_get, name="test_submit")
    router.add_post("/submit", h.test_submit_post)