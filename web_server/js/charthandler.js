//------------- DATA FOR ALL CHARTS ------------------


const dataH1 = {
labels: [],
datasets: [{
  label: 'Heel 1',
  data: [],
  fill: false,
  borderColor: 'rgb(75, 192, 192)',
  tension: 0
}]
};

const dataH2 = {
labels: [],
datasets: [{
  label: 'Heel 2',
  data: [],
  fill: false,
  borderColor: 'rgb(75, 192, 192)',
  tension: 0
}]
};

const dataB11 = {
labels: [],
datasets: [{
  label: 'Ball 1 1',
  data: [],
  fill: false,
  borderColor: 'rgb(75, 192, 192)',
  tension: 0
}]
};

const dataB21 = {
labels: [],
datasets: [{
  label: 'Ball 2 1',
  data: [],
  fill: false,
  borderColor: 'rgb(75, 192, 192)',
  tension: 0
}]
};

const dataB12 = {
labels: [],
datasets: [{
  label: 'Ball 1 2',
  data: [],
  fill: false,
  borderColor: 'rgb(75, 192, 192)',
  tension: 0
}]
};

const dataB22 = {
labels: [],
datasets: [{
  label: 'Ball 2 2',
  data: [],
  fill: false,
  borderColor: 'rgb(75, 192, 192)',
  tension: 0
}]
};


settings = {
  scales: {
    x: {
      title: {
        display: true,
        text: "Time (s)",
        font: {
          size: 20
        }
      }
    }
  },
  animation: {
    duration: 100
  }
}


//------------- CHART INITIALIZIATION -----------------

const ctx = document.getElementById("Heel1");
const chartH1 = new Chart(ctx, {type: "line", data:dataH1, options: settings});
const ctx2 = document.getElementById("Heel2");
const chartH2 = new Chart(ctx2, {type: "line", data:dataH2, options: settings});

const ctx3 = document.getElementById("Ball11");
const chartB11 = new Chart(ctx3, {type: "line", data:dataB11, options: settings});
const ctx4 = document.getElementById("Ball21");
const chartB21 = new Chart(ctx4, {type: "line", data:dataB21, options: settings});

const ctx5 = document.getElementById("Ball12");
const chartB12 = new Chart(ctx5, {type: "line", data:dataB12, options: settings});
const ctx6 = document.getElementById("Ball22");
const chartB22 = new Chart(ctx6, {type: "line", data:dataB22, options: settings});

const boss_socket = new WebSocket("ws://sock_boss.local:80/ws");

boss_socket.addEventListener("message", (event) => {
  console.log("Message from server ", event.data);
});


//------------- UPDATE FUNCTIONS ----------------------


function addData(chart, label, newData) {
  chart.data.labels.push(label);
  chart.data.datasets.forEach((dataset) => {
    dataset.data.push(newData);
  });
  
  chart.update();
  
  if (chart.data.labels.length>150) {
    chart.data.labels.shift();
    chart.data.datasets.forEach((dataset) => {
      dataset.data.shift();
    });
    chart.update();
  }
}




//------------ DATA POLLER -----------------------

async function sendPoll() {
  const url = "http://sock_boss.local";
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Response status: ${response.status}`);
    }

    const result = await response.json();
    console.log(result);
    return result;
  } catch (error) {
    console.error(error.message);
  }
}

async function updateData() {
    const result = await sendPoll();
    const timestamp = result["time"] / 1000;
    addData(chartH1,timestamp,result["heel1"]);
    addData(chartH2,timestamp,result["heel2"]);
    addData(chartB11,timestamp,result["ball11"]);
    addData(chartB21,timestamp,result["ball21"]);
    addData(chartB12,timestamp,result["ball12"]);
    addData(chartB22,timestamp,result["ball22"]);
}

var updater = window.setInterval(updateData, 100);