

// When <li> clicked send id to backend
document.querySelector('#directions-list').addEventListener('click', async function (e) {
    if (e.target.classList.contains('directions-button')) {
        const placeId = e.target.closest('li').id;
        const originAddress = document.querySelector('h2').id;

        const res = await axios.post('/search/details', {
            'destination_id': placeId,
            'origin_address': originAddress
        });
        const dist = res.data.routes[0].legs[0].distance.text;
        const steps = res.data.routes[0].legs[0].steps;

        appendDirections(steps, dist);
    }

    if (e.target.classList.contains('forecast-button')) {
        const coords = e.target.closest('li').getAttribute('data-coords');
        const forecast_res = await axios.post('/search/forecast', {
            'coords': coords
        })

        appendForecast(forecast_res)
    }
});

function appendDirections(steps, dist) {
    const locationList = document.querySelector('#location-directions');
    const totalDistance = document.createElement('p');
    locationList.innerHTML = '';
    totalDistance.innerText = `Total Distance: ${dist}`;
    locationList.append(totalDistance);

    for (let i = 0; i < steps.length; i++) {
        const direction = steps[i].html_instructions;
        const stepDist = steps[i].distance.text;
        const stepDuration = steps[i].duration.text;
        const stepManuever = steps[i].maneuver;

        const directionPara = document.createElement('p');
        directionPara.innerHTML = `<b>Step ${[i + 1]}: </b>${direction}`;

        const distPara = document.createElement('p');
        distPara.innerHTML = `<b>Distance: </b>${stepDist}`;

        const durationPara = document.createElement('p');
        durationPara.innerHTML = `<b>Estimated Time: </b> ${stepDuration}`;

        listElement = document.createElement('li');
        listElement.append(directionPara);
        listElement.append(distPara);
        listElement.append(durationPara);

        if (i > 0) {
            const manueverPara = document.createElement('p');
            manueverPara.innerHTML = `<b>Manuever: </b>${stepManuever}`;
            listElement.append(manueverPara)
        }

        locationList.append(listElement);
    }
}

// Object Oriented?



function appendForecast(forecast) {
    // console.log(forecast)
    const forecastDisplay = document.querySelector('#forecast-display')
    const forecastList = forecast.data.list
    forecastDisplay.innerHTML = ''

    for (let i = 0; i < forecastList.length; i++) {
        const datetime = forecastList[i].dt_txt
        const cloudCover = forecastList[i].clouds.all
        const humidity = forecastList[i].main.humidity
        const tempKelvin = forecastList[i].main.temp
        const temp = Math.round(((tempKelvin - 273.15) * 1.8) + 32)
        const description = forecastList[i].weather[0].description
        const wind = forecastList[i].wind.speed

        const datetimePara = document.createElement('p');
        datetimePara.innerHTML = `<b>Date: </b>${datetime}`;

        const cloudCoverPara = document.createElement('p');
        cloudCoverPara.innerHTML = `<b>Cloud Cover (%): </b> ${cloudCover}`;

        const humidityPara = document.createElement('p');
        humidityPara.innerHTML = `<b>Humidity (%): </b>${humidity}`;

        const tempPara = document.createElement('p');
        tempPara.innerHTML = `<b>Temperature (F): </b>${temp}`;

        const descriptionPara = document.createElement('p');
        descriptionPara.innerHTML = `<b>Weather: </b>${description}`;

        const windPara = document.createElement('p');
        windPara.innerHTML = `<b>Windspeed (mph): </b>${wind}`;

        listElement = document.createElement('li');
        listElement.append(datetimePara);
        listElement.append(cloudCoverPara);
        listElement.append(humidityPara);
        listElement.append(tempPara);
        listElement.append(descriptionPara);
        listElement.append(windPara);

        forecastDisplay.append(listElement)
    }
}

// function appendWeather(weather) {
//     console.log(weather)
// }

// if (e.target.classList.contains('weather-button')) {
//     const coords = e.target.closest('li').getAttribute('data-coords');
//     const weather_res = await axios.post('/search/weather', {
//         'coords': coords
//     })

//     appendWeather(weather_res)
// }





