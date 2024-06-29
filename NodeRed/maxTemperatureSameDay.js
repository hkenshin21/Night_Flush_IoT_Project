/*This gets the max temperature from the json forecast file
fetched with http get. Temperature for the same day is used when calculating desired indoor temp*/
const get_max_temp_next_day = (data) => {
    let max_temp = null;
    const now = new Date();
   
    data.timeSeries.forEach(entry => {
        const valid_time = new Date(entry.validTime);
        if (valid_time.getFullYear() === now.getFullYear() &&
            valid_time.getMonth() === now.getMonth() &&
            valid_time.getDate() === now.getDate()) {
            entry.parameters.forEach(param => {
                if (param.name === 't') {
                    const temp = param.values[0];
                    if (max_temp === null || temp > max_temp) {
                        max_temp = temp;
                    }
                }
            });
        }
    });

    return max_temp;
};

// Use the function with the msg.payload
const data = msg.payload;
const maxTemp = get_max_temp_next_day(data);
msg.payload = maxTemp;
return msg;

