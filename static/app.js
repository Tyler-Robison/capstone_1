

// When <li> clicked send id to backend
document.querySelector('#directions-container').addEventListener('click', async function (e) {
    if (e.target.classList.contains('directions-button')) {
        const placeId = e.target.closest('div').id;
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
        const coords = e.target.closest('div').getAttribute('data-coords');
        const forecast_res = await axios.post('/search/forecast', {
            'coords': coords
        })

        appendForecast(forecast_res)
    }
});

function appendDirections(steps, dist) {
    const locationList = document.querySelector('#location-directions');
    locationList.innerHTML = '';
    const h2 = document.createElement('h2')
    h2.innerText = 'Directions'
    h2.style.marginLeft = '25%'
    locationList.append(h2)
    const totalDistance = document.createElement('p');
    totalDistance.innerHTML = `<b>Total Distance: </b>${dist}`;
    locationList.append(totalDistance);

    // Loop through list array, make each step an <li>
    for (let i = 0; i < steps.length; i++) {
        const direction = steps[i].html_instructions;
        const stepDist = steps[i].distance.text;
        const stepDuration = steps[i].duration.text;
        const stepManuever = steps[i].maneuver;

        const directionPara = document.createElement('p');
        directionPara.innerHTML = `${direction}`;

        const distPara = document.createElement('p');
        distPara.innerHTML = `<b>Distance: </b>${stepDist}`;

        const durationPara = document.createElement('p');
        durationPara.innerHTML = `<b>Estimated Time: </b> ${stepDuration}`;

        listElement = document.createElement('li');
        listElement.append(directionPara);
        listElement.append(distPara);
        listElement.append(durationPara);

        // Some steps have undefined manuever
        if (stepManuever !== undefined) {
            const manueverPara = document.createElement('p');
            manueverPara.innerHTML = `<b>Manuever: </b>${stepManuever}`;
            listElement.append(manueverPara)
        }

        locationList.append(listElement);
        // Don't want <hr> on bottom <li>
        if (i < steps.length - 1) {
            const hr = document.createElement('hr');
            locationList.append(hr)
        }
    }
    const directionDiv = document.querySelector('#directions-div');
    directionDiv.classList.remove('invisible')
}

// Object Oriented?

function appendForecast(forecast) {
    
    const forecastDisplay = document.querySelector('#forecast-display')
    const forecastList = forecast.data.list
    forecastDisplay.innerHTML = ''
    const h2 = document.createElement('h2')
    h2.innerText = 'Forecast'
    h2.style.marginLeft = '30%'
    forecastDisplay.append(h2)


    for (let i = 0; i < forecastList.length; i++) {
        const datetime = forecastList[i].dt_txt
        const dateArr = datetime.split(' ');
        const time = convertTime(dateArr[1]);
        const dateStr = `${dateArr[0]}`
        const timeStr = `${time}`
        const cloudCover = forecastList[i].clouds.all
        const humidity = forecastList[i].main.humidity
        const tempKelvin = forecastList[i].main.temp
        const temp = Math.round(((tempKelvin - 273.15) * 1.8) + 32)
        const description = forecastList[i].weather[0].description
        const wind = forecastList[i].wind.speed

        const datePara = document.createElement('p');
        datePara.innerHTML = `<b>Date: </b>${dateStr}`;

        const timePara = document.createElement('p');
        timePara.innerHTML = `<b>Time: </b>${timeStr}`;

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

        listDiv = document.createElement('div');
        listDiv.append(datePara);
        listDiv.append(timePara);
        listDiv.append(cloudCoverPara);
        listDiv.append(humidityPara);
        listDiv.append(tempPara);
        listDiv.append(descriptionPara);
        listDiv.append(windPara);
        listDiv.style.paddingLeft = '5%'

        forecastDisplay.append(listDiv)
        if (i < forecastList.length - 1) {
            const hr = document.createElement('hr');
            forecastDisplay.append(hr)
        }
    }
    const forecastDiv = document.querySelector('#forecast-div');
    forecastDiv.classList.remove('invisible')
}

function convertTime(militaryTime) {
    return moment(militaryTime, 'HH:mm:ss').format('h:mm A');
}


