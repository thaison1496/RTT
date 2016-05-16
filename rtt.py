import csv
import pprint
import plotly
import plotly.graph_objs as go
from plotly.graph_objs import Scatter, Layout

# Create random data with numpy
import numpy as np

client = '192.168.1.102'
server = '128.119.245.12'
packets = []
data_packets = []
ack_packets = []
result = []


def extract_data(packet):
	if (packet['src'] != client):
		return []
	expected_ack = 0
	for word in packet['info'].split():
		if ((word[:4] == 'Seq=') or (word[:4] == 'Len=')):
			expected_ack += (int)(word[4:])
	if (expected_ack > 1):
		return [{
			'no': packet['no'],
			'expected_ack': expected_ack
			}]
	else:
		return []


def extract_ack(packet):
	if (packet['src'] != server):
		return []
	ack = 0
	for word in packet['info'].split():
		if (word[:4] == 'Ack='):
			ack += (int)(word[4:])
	if (ack > 1):
		return [{
			'no': packet['no'],
			'ack': ack
			}]
	else:
		return []


def match(data_packets, ack_packets):
	result = []
	for data_packet in data_packets:
		for ack_packet in ack_packets:
			if (data_packet['expected_ack'] == ack_packet['ack']):
				result.append({
						'packet': data_packet['no'],
						'ack': ack_packet['no'],
						'rtt': packets[ack_packet['no']]['time'] - packets[data_packet['no']]['time'],
						'time': packets[data_packet['no']]['time']
					})
				break
	return result


def draw(result):
	time = []
	rtt = []
	estRTT = []
	for line in result:
		time.append(line['time'])
		rtt.append(line['rtt'])
		estRTT.append(line['estRTT'])

	# Create traces
	trace0 = go.Scatter(
	    x = time,
	    y = rtt,
	    mode = 'lines+markers',
	    name = 'RTT'
	)
	trace1 = go.Scatter(
	    x = time,
	    y = estRTT,
	    mode = 'lines+markers',
	    name = 'estRTT'
	)
	data = [trace0, trace1]

	# Plot and embed in ipython notebook!
	plotly.offline.plot({
		'data': data, 
		'layout': Layout(
    		title="RTT and Estimated RTT"
	)})



file = open('nn2.csv', 'r')
reader = csv.reader(file)
next(reader, None)

for line in reader:
	packet = {
			"no": (int)(line[0]),
			"time" : (float)(line[1]),
			"src" : line[2],
			"dest" : line[3],
			"info" : line[6]
		}
	packets.append(packet)
	data_packets += extract_data(packet)
	ack_packets += extract_ack(packet)

result = match(data_packets, ack_packets)
result = result[:len(result) - 1] #exception for last packets

#calculate estimated RTT after each sample
result[0]['estRTT'] = result[0]['rtt']
for i in range(1,len(result)):
	result[i]['estRTT'] = result[i-1]['estRTT'] * 0.875 + result[i]['rtt'] * 0.125

draw(result)

pprint.pprint(result)


