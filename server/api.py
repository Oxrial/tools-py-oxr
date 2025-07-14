def create_api(app):
    @app.route('/api/files', methods=['GET'])
    def list_files():
        import os
        path = os.path.join(os.path.expanduser('~'), 'Documents')
        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        return {'files': files[:10]}