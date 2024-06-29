/*This gets the max temperature from the json forecast file
fetched with http get. Temperature for next day is used when calculating desired indoor temp*/
const get_max_temp_next_day = (data) => {
    let max_temp = null;
    const now = new Date();
    //define next day (add 1 day to today)
    const next_day = new Date(now.getFullYear(), now.getMonth(), now.getDate() + 1);

    data.timeSeries.forEach(entry => {
        const valid_time = new Date(entry.validTime);
        if (valid_time.getFullYear() === next_day.getFullYear() &&
            valid_time.getMonth() === next_day.getMonth() &&
            valid_time.getDate() === next_day.getDate()) {
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

