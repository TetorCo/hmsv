from fastapi import FastAPI, Form, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from app.main import arima
from monitoring.monitoring import instrumentator

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
instrumentator.instrument(app).expose(app, include_in_schema=False, should_gzip=True)


@app.get("/")
def mainPage(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/guide")
def subPage(request: Request):
    return templates.TemplateResponse("guide.html", {"request": request})


@app.get('/predict')
def subPage2(request: Request):
    return templates.TemplateResponse("predict_fastapi.html", context={"request": request})


@app.post('/predict')
def predict_model(request: Request,
                stockname: str = Form(...),
                dr: str = Form(...),
                tgr: str = Form(...),
                mos: str = Form(...),
                price: str = Form(...),
                count: str = Form(...)):

    try:
        arima_predict = arima(stockname,
                            int(dr),
                            int(tgr),
                            int(mos),
                            float(price),
                            int(count))

        result_data = arima_predict.predict()

        if result_data != False:
            return templates.TemplateResponse("result_fastapi.html", {"request": request, "result_data": result_data})

        else:
            return templates.TemplateResponse("fail.html", {"request": request})

    except:
        return templates.TemplateResponse("fail.html", {"request": request})


@app.get("/fail")
def testPage(request: Request):
    return templates.TemplateResponse("fail.html", {"request": request})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5000)