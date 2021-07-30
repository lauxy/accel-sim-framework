#!/usr/bin/env python

import json
import csv
import pandas as pd
import numpy
import os 
import collections 
import glob
import sys
from os.path import dirname, basename, isfile, join
import shutil

configs = []
all_configs = ['volta_sass_sim', 'volta_sass_hw', 'volta_sass_hybrid', 'volta_ptx_sim']
if (len(sys.argv) > 1):
	if(str(sys.argv[1]) == 'all'):
		configs = all_configs
	elif (str(sys.argv[1]) in all_configs):
		configs.append(str(sys.argv[1]))
	else:
		print "Please enter AccelWattch config: One of [volta_sass_sim,volta_sass_hw,volta_sass_hybrid,volta_ptx_sim] or 'all'"
		exit()
else:
	print "Please enter AccelWattch config: One of [volta_sass_sim,volta_sass_hw,volta_sass_hybrid,volta_ptx_sim] or 'all'"
	exit()

power_counters = ['IBP,', 'ICP,', 'DCP,', 'TCP,', 'CCP,', 'SHRDP,', 'RFP,', 
				'INTP,', 'FPUP,', 'DPUP,', 'INT_MUL24P,', 'INT_MUL32P,', 'INT_MULP,','INT_DIVP,', 'FP_MULP,',
	            'FP_DIVP,', 'FP_SQRTP,', 'FP_LGP,', 'FP_SINP,', 'FP_EXP,','DP_MULP,', 'DP_DIVP,', 'TENSORP,', 'TEXP,',                                  
	            'SCHEDP,', 'L2CP,', 'MCP,', 'NOCP,', 'DRAMP,','PIPEP,', 'IDLE_COREP,', 'CONSTP','STATICP','kernel_avg_power']

rootdir = os.getcwd();
results_dir = rootdir + '/accelwattch_results'
if os.path.exists(results_dir):
	shutil.rmtree(results_dir, ignore_errors=True)
os.mkdir(results_dir)

for config in configs:
	reportspath = rootdir + '/accelwattch_power_reports/' + config
	power_dict = collections.OrderedDict()
	for kernelVer in [1,2]:
		kernelnames = {}
		benchmarks = []
		if (kernelVer == 1):
			kernelnames = { 'backprop-rodinia-3.1' : '_Z22bpnn_layerforward_CUDAPfS_S_S_ii',
							'binomialOptions' : '_Z21binomialOptionsKernelv',
							'b+tree-rodinia-3.1' : 'findRangeK',
							'dct8x8' : '_Z14CUDAkernel1DCTPfiiiy',
							'fastWalshTransform' : '_Z15fwtBatch2KernelPfS_i',
							'histogram' : '_Z17histogram64KernelPjP5uint4j',
							'hotspot-rodinia-3.1' : '_Z14calculate_tempiPfS_S_iiiiffffff',
							'kmeans-rodinia-3.1' : '_Z11kmeansPointPfiiiPiS_S_S0_',
							'mergeSort' : '_Z30mergeElementaryIntervalsKernelILj1EEvPjS0_S0_S0_S0_S0_jj',
							'pathfinder-rodinia-3.1' : '_Z14dynproc_kerneliPiS_S_iiii',
							'quasirandomGenerator' : '_Z26quasirandomGeneratorKernelPfjj',
							'SobolQRNG' : '_Z15sobolGPU_kerneljjPjPf',
							'srad_v1-rodinia-3.1' : '_Z4sradfiilPiS_S_S_PfS0_S0_S0_fS0_S0_',
							'parboil-mri-q' : '_Z12ComputeQ_GPUiiPfS_S_S_S_',	
							'parboil-sad' : '_Z11mb_sad_calcPtS_ii',
							'parboil-sgemm' : '_Z9mysgemmNTPKfiS0_iPfiiff',	
							'cutlass_perf_test___seed_2020___dist_0____m_2560___n_16___k_2560___kernels_wmma_gemm_nn____iterations_5___providers_cutlass' : '',
							'cutlass_perf_test___seed_2020___dist_0____m_4096___n_128___k_4096___kernels_wmma_gemm_nn____iterations_5___providers_cutlass' : '',
							'cutlass_perf_test___seed_2020___dist_0____m_2560___n_512___k_2560___kernels_wmma_gemm_nn____iterations_5___providers_cutlass' : '',
							'cudaTensorCoreGemm' : '',
							}
		else:
			kernelnames = { 'backprop-rodinia-3.1' : '_Z24bpnn_adjust_weights_cudaPfiS_iS_S_',
							'binomialOptions' : '_Z21binomialOptionsKernelv',
							'b+tree-rodinia-3.1' : 'findK',
							'dct8x8' : '_Z14CUDAkernel2DCTPfS_i',
							'fastWalshTransform' : '_Z15fwtBatch1KernelPfS_i',
							'histogram' : '_Z18histogram256KernelPjS_j',
							'hotspot-rodinia-3.1' : '_Z14calculate_tempiPfS_S_iiiiffffff',
							'kmeans-rodinia-3.1' : '_Z11kmeansPointPfiiiPiS_S_S0_',
							'mergeSort' : '_Z21mergeSortSharedKernelILj1EEvPjS0_S0_S0_j',
							'pathfinder-rodinia-3.1' : '_Z14dynproc_kerneliPiS_S_iiii',
							'quasirandomGenerator' : '_Z16inverseCNDKernelPfPjj',
							'SobolQRNG' : '_Z15sobolGPU_kerneljjPjPf',
							'srad_v1-rodinia-3.1' : '_Z4sradfiilPiS_S_S_PfS0_S0_S0_fS0_S0_',	
							'parboil-mri-q' : '_Z12ComputeQ_GPUiiPfS_S_S_S_',	
							'parboil-sad' : '_Z11mb_sad_calcPtS_ii',
							'parboil-sgemm' : '_Z9mysgemmNTPKfiS0_iPfiiff',
							'cutlass_perf_test___seed_2020___dist_0____m_2560___n_16___k_2560___kernels_wmma_gemm_nn____iterations_5___providers_cutlass' : '',
							'cutlass_perf_test___seed_2020___dist_0____m_4096___n_128___k_4096___kernels_wmma_gemm_nn____iterations_5___providers_cutlass' : '',	
							'cutlass_perf_test___seed_2020___dist_0____m_2560___n_512___k_2560___kernels_wmma_gemm_nn____iterations_5___providers_cutlass' : '',
							'cudaTensorCoreGemm' : '',
							}

		for dirname in os.listdir(reportspath):
			benchmarks.append(dirname[:-4])

		if(kernelVer != 1):
			if 'binomialOptions' in benchmarks:
				benchmarks.remove('binomialOptions')
			if 'hotspot-rodinia-3.1' in benchmarks:
				benchmarks.remove('hotspot-rodinia-3.1')
			if 'histogram' in benchmarks:
				benchmarks.remove('histogram')
			if 'kmeans-rodinia-3.1' in benchmarks:
				benchmarks.remove('kmeans-rodinia-3.1')
			if 'pathfinder-rodinia-3.1' in benchmarks:
				benchmarks.remove('pathfinder-rodinia-3.1')
			if 'SobolQRNG' in benchmarks:
				benchmarks.remove('SobolQRNG')
			if 'srad_v1-rodinia-3.1' in benchmarks:
				benchmarks.remove('srad_v1-rodinia-3.1')
			if 'parboil-mri-q' in benchmarks:
				benchmarks.remove('parboil-mri-q')
			if 'parboil-sad' in benchmarks:
				benchmarks.remove('parboil-sad')
			if 'parboil-sgemm' in benchmarks:
				benchmarks.remove('parboil-sgemm')
			if 'cutlass_perf_test___seed_2020___dist_0____m_2560___n_16___k_2560___kernels_wmma_gemm_nn____iterations_5___providers_cutlass' in benchmarks:
				benchmarks.remove('cutlass_perf_test___seed_2020___dist_0____m_2560___n_16___k_2560___kernels_wmma_gemm_nn____iterations_5___providers_cutlass')
			if 'cutlass_perf_test___seed_2020___dist_0____m_4096___n_128___k_4096___kernels_wmma_gemm_nn____iterations_5___providers_cutlass' in benchmarks:
				benchmarks.remove('cutlass_perf_test___seed_2020___dist_0____m_4096___n_128___k_4096___kernels_wmma_gemm_nn____iterations_5___providers_cutlass')
			if 'cutlass_perf_test___seed_2020___dist_0____m_2560___n_512___k_2560___kernels_wmma_gemm_nn____iterations_5___providers_cutlass' in benchmarks:
				benchmarks.remove('cutlass_perf_test___seed_2020___dist_0____m_2560___n_512___k_2560___kernels_wmma_gemm_nn____iterations_5___providers_cutlass')
			if 'cudaTensorCoreGemm' in benchmarks:
				benchmarks.remove('cudaTensorCoreGemm')
		
		if config == "volta_ptx_sim":
			if 'cutlass_perf_test___seed_2020___dist_0____m_2560___n_16___k_2560___kernels_wmma_gemm_nn____iterations_5___providers_cutlass' in benchmarks:
				benchmarks.remove('cutlass_perf_test___seed_2020___dist_0____m_2560___n_16___k_2560___kernels_wmma_gemm_nn____iterations_5___providers_cutlass')
			if 'cutlass_perf_test___seed_2020___dist_0____m_4096___n_128___k_4096___kernels_wmma_gemm_nn____iterations_5___providers_cutlass' in benchmarks:
				benchmarks.remove('cutlass_perf_test___seed_2020___dist_0____m_4096___n_128___k_4096___kernels_wmma_gemm_nn____iterations_5___providers_cutlass')
			if 'cutlass_perf_test___seed_2020___dist_0____m_2560___n_512___k_2560___kernels_wmma_gemm_nn____iterations_5___providers_cutlass' in benchmarks:
				benchmarks.remove('cutlass_perf_test___seed_2020___dist_0____m_2560___n_512___k_2560___kernels_wmma_gemm_nn____iterations_5___providers_cutlass')
		
		if config == "volta_sass_hybrid" or config == "volta_sass_hw":
			if 'pathfinder-rodinia-3.1' in benchmarks:
				benchmarks.remove('pathfinder-rodinia-3.1')

		kernel_count = 0
		
		for benchmark in benchmarks:
			if benchmark not in kernelnames:
				continue

			f = open((reportspath + '/' + benchmark + '.log'), 'r')
			x = f.readlines()
			baseline = collections.OrderedDict()
			kernel_count = 0
			kernelname = 'kernel_name=' + kernelnames[benchmark]
			for each in power_counters:
				baseline[each] = 0
			benchmark_idx = (benchmark + '_k' + str(kernelVer))
			power_dict[benchmark_idx] = collections.OrderedDict()
			for each in range(len(x)):
				x[each] = x[each].replace(" ", "")
			for each in range(len(x)):
				if (x[each].find(kernelname) != -1):
					kernel_count += 1
					key,value = x[each+4].split('=')
					value = value.rstrip('\n')
					baseline[(key)] += float(value)
					for stat in range(5,38):
						key,value = x[each+stat].split('=')
						value = value.rstrip('\n')
						baseline[(key[8:])] += float(value)

			if(kernel_count != 0):
				
				for each in power_counters:
					#power_dict[benchmark_idx][each] = float(baseline[each])
					power_dict[benchmark_idx][each] = float(baseline[each]) / float(kernel_count)
				power_dict[benchmark_idx]['DRAMP,'] = power_dict[benchmark_idx]['DRAMP,'] + power_dict[benchmark_idx]['MCP,']
				power_dict[benchmark_idx]['L2CP,'] = power_dict[benchmark_idx]['L2CP,'] + power_dict[benchmark_idx]['NOCP,']
				if config == "volta_ptx_sim":
					for each in ['MCP,','NOCP,']:
						del power_dict[benchmark_idx][each] # PTX model doesnt need these counters anymore
				else:
					for each in ['MCP,','TCP,','INT_MUL24P,','INT_MUL32P,','INT_DIVP,','FP_DIVP,','DP_DIVP,','NOCP,']:
						del power_dict[benchmark_idx][each] # SASS model doesnt need these counters anymore
			else:
				print "Warning: " + benchmark_idx + " has no simulator data." 

	os.chdir(results_dir)
	df = pd.DataFrame.from_dict(power_dict, orient='index')
	cwd = 'accelwattch_'+config+ '.csv'
	df.to_csv(cwd)
	os.chdir(rootdir)
