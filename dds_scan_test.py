import exp.exp_dds_scan_test as experiment

params = Params('amp;V', 'freq;Hz', 'pi_len;s')

params.amp.value = 1.0
params.freq.value = 2*MHz

params.pi_len.value = np.linspace(us,2*us, 1001)
    
# fig_ref = plt.figure() 
fig_ref = None

try:    
    scan(lab, params, experiment, fig=fig_ref)

except:
    error_manager()
    





