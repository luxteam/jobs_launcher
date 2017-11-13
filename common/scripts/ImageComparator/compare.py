#!usr/bin/env python
import sys
import os
import argparse

import CompareMetrics

def createArgParser():
	argparser = argparse.ArgumentParser(description='''Parser desctiption''')
	argparser.add_argument('--nrmsd', action='store_true', default=False)
	argparser.add_argument('--manhattan', action='store_true', default=False)
	argparser.add_argument('--nvidea', action='store_true', default=False)
	argparser.add_argument('--correlation', action='store_true', default=False)
	argparser.add_argument('--hamming', action='store_true', default=False)
	argparser.add_argument('--chebyshev', action='store_true', default=False)
	argparser.add_argument('--euclidean', action='store_true', default=False)
	argparser.add_argument('--squeclidean', action='store_true', default=False)
	argparser.add_argument('--cosine', action='store_true', default=False)
	argparser.add_argument('--canberra', action='store_true', default=False)
	argparser.add_argument('--braycurtis', action='store_true', default=False)
	argparser.add_argument('--pillowdiff', action='store_true', default=True)
	
	argparser.add_argument('file1')
	argparser.add_argument('file2')
	argparser.add_argument('--tolerance', type=int, default=3)

	return argparser


def tryNvidea(file1, file2):
	try:
		os.system('imf_diff.exe %s %s' % (file1, file2))
	except FileNotFoundError:
		print ('imf_diff not found')
		

def main():
	args = createArgParser()

	file1 = args.parse_args().file1
	file2 = args.parse_args().file2
	tolerance = args.parse_args().tolerance

	metrics = CompareMetrics.CompareMetrics(file1, file2)

	if args.parse_args().pillowdiff:
		print ("{}%".format(metrics.getDiffPixeles(tolerance)))

	if args.parse_args().nrmsd:
		print (metrics.getNrmsd())
	if args.parse_args().hamming:
		print (metrics.getHamming())
	if args.parse_args().chebyshev:
		print (metrics.getChebyshev())
	if args.parse_args().manhattan:
		print (metrics.getManhattan())
	if args.parse_args().correlation:
		print (metrics.getCorrelation())
	if args.parse_args().euclidean:
		print (metrics.getEuclidean())
	if args.parse_args().squeclidean:
		print (metrics.getSqueclidean())
	if args.parse_args().cosine:
		print (metrics.getCosine())
	if args.parse_args().canberra:
		print (metrics.getCanberra())
	if args.parse_args().braycurtis:
		print (metrics.getBraycurtis())

if __name__ == '__main__':
	main()