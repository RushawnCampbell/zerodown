from frontend.App import App
from waitress import serve
if __name__ == "__main__":
    app = App()
    app.mainloop()
    serve(app, host='127.0.0.1', port=8080, threads=2) #WAITRESS!
    
