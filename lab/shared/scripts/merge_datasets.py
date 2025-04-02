import os
from datetime import datetime

# Function that opens a csv file and saves the content in a list, where each element is a list of the elements of a row
def get_content(filepath):
    file = open(filepath, "r", encoding="UTF-8")
    out = []
    for line in file:
        out.append(line.strip().split(","))
    return out

# Function that appends a list of lists, where each list is a row, to the specified file
def add_rows(rows, outpath):
    file = open(outpath, "a", encoding="UTF-8")
    for line in rows[1:]:
        line_str = ",".join(str(x) for x in line)
        file.write(line_str+"\n")
    file.close()

# Function that, given a string representing a date, returns the corresponding time in microseconds
def to_timestamp(string):
    date_format = '%Y-%m-%d %H:%M:%S.%f'
    if "." not in string: string += ".000000"
    return datetime.strptime(string,date_format).timestamp()*(10**6)

# Function that update the timestamps of the row in input, given the last "valid" timestamp in the output file
# and the difference between the timestamp of this row and the timestamp of the first row of the input file
def update_timestamp(last, line, delta_abs):

    # 28 --> timestamp of the first packet of the connection; 29 --> timestamp of the last packet of the connection;
    # 33 --> timestamp of the SYN packet in the connection; 34 --> timestamp of the SYN-ACK packet in the connection; 
    # 35 --> timestamp of the ACK packet in the connection
    if last == 0: return
    last = to_timestamp(last)
    date_to_conv = [line[28], line[29], line[33] if line[33] != "" and line[33] != "-" else "", line[34] if line[34] != "" and line[34] != "-" else "", line[35] if line[35] != "" and line[35] != "-" else ""]
    dates = [to_timestamp(x) for x in date_to_conv if x != ""] # list containing every timestamp of the line expressed in microseconds
    if dates[0] - last > 1000000.0:                            # update the timestamps if the difference between the last timestamp of the output file and the timestamp of this line is greater than 1 second
        deltas = [dates[i]-dates[0] for i in range(1,len(dates))]
        deltas.insert(0, 0.0)
        new_times = [last + 1000000.0 + delta_abs + d for d in deltas]  # compute the new value for the timestamps
        date_conv = []
        ind = 0
        for date in date_to_conv:
            if date != "":  # Computes the corresponding date value for the updated timestamps
                date_conv.append(datetime.strftime(datetime.fromtimestamp(new_times[ind]/10**6), '%Y-%m-%d %H:%M:%S.%f'))
                ind += 1
            else: date_conv.append("-")
        line[28] = date_conv[0]   # update the values in the line
        line[29] = date_conv[1]
        line[33] = date_conv[2]
        line[34] = date_conv[3]
        line[35] = date_conv[4]
    return line

if __name__ == '__main__':

    outfile_path = "shared/logs/dataset.csv"        # File to be written
    input_file_path = "shared/logs/allowed3.csv"    # Path of the file that will be appended
    rows = get_content(input_file_path)
    outfile = open(outfile_path, "r")
    outfile.seek(0, os.SEEK_END)
    if outfile.tell():                              # Check if the output file is empty, in that case the rows will be directly inserted
        outfile.seek(0)
        lastline = outfile.readlines()[-1].strip().split(",")    # Get the last line of the file
        last_time = lastline[28]                    # First packet's timestamp of the last row (i.e. of the last connection)
        first = to_timestamp(rows[1][28])           # First packet's timestamp of the first row in the input file
        ind = 1
        for line in rows[1:]:                       # Update each row updating every timestamp
            line_time = to_timestamp(line[28])
            rows[ind] = update_timestamp(last_time, line, line_time-first)
            ind+=1
    outfile.close()
    add_rows(rows, outfile_path)                    # Insert the updated rows in the output file