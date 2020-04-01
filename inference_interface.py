import numpy as np
import h5py
from datetime import datetime
from json import dumps, loads
from glob import glob

try:
    import multihist as mh
    HAVE_MULTIHIST = True
except ImportError:
    HAVE_MULTIHIST = False

try:
    import ROOT as rt
    import root_numpy
    HAVE_ROOT = True
except ImportError:
    HAVE_ROOT = False


def concatenate_nTtoys(file_names=[],
                       output_name="file.hdf5",
                       enforce_equal_version=True):
    """
        function that takes one or more inference toy datasets
        and concatenates into one long file.
        if enforce_equal_version, the functoin will throw error
        if the versions are unequal
    """
    raise NotImplementedError()


def concatenate_fits(file_names=[], output_name="file.hdf5"):
    """
        Function that takes list of fit results,
        concatenates the results and stores the result in output_name.
        if enforce_equal_version, the functoin will throw error
        if the versions are unequal
    """
    raise NotImplementedError()


def template_to_multihist(file_name, hist_name=None):
    """
        Function that loads a template into the multihist format
        str file_name : name of template file
        str hist_name: name of template, if None, take the first
    """
    if not HAVE_MULTIHIST:
        raise NotImplementedError("template_to_multihist requires multihist")

    bins = []
    bin_names = []
    with h5py.File(file_name, "r") as f:
        for i, (k, b) in enumerate(sorted(f["bins"].items())):
            bins.append(np.array(b))
            bn = b.attrs.get("name", "axis{:d}".format(i))
            bin_names.append(bn)
        ret = mh.Histdd(bins=bins, axis_names=bin_names)
        if hist_name is None:
            ret.histogram = np.array(next(iter(f["templates"].values())))
        else:
            ret.histogram = np.array(f["templates/"+hist_name])
    return ret


def multihist_to_template(histograms, file_name, histogram_names=None,metadata={"version":"0.0","date":datetime.now().strftime('%Y%m%d_%H:%M:%S')}):
    if not HAVE_MULTIHIST:
        raise NotImplementedError("template_to_multihist requires multihist")
    if histogram_names is None: 
        histogram_names = ["%i" for i in range(len(histograms))]
    with h5py.File(file_name, "w") as f:
        for k,i in metadata.items():
            f.attrs[k] = i
        bins = histograms[0].bin_edges
        axis_names = histograms[0].axis_names
        if axis_names is None:
            axis_names = ["" for i in range(len(bins))]
        for i, (b, bn) in enumerate(zip(bins, axis_names)):
            dset = f.create_dataset("bins/{:d}".format(i), data=b)
            dset.attrs["name"] = bn 

        for histogram, histogram_name in zip(histograms, histogram_names):
            dset = f.create_dataset("templates/{:s}".format(histogram_name), data=histogram.histogram)


def get_root_hist_axis_labels(hist):
    dim = hist.GetDimension()
    if dim ==1: 
        axes [hist.GetXaxis()]
    elif dim ==2: 
        axes = [hist.GetXaxis(), hist.GetYaxis()]
    elif dim ==3: 
        axes = [hist.GetXaxis(), hist.GetYaxis(), hist.GetZaxis()]
    else: 
        axes = [hist.GetAxis(i) for i in range(dim)]
    ret = [ax.GetName() for ax in axes]
    print("ret is",ret)
    return ret

def set_root_hist_axis_labels(hist, axis_names):
    dim = hist.GetDimension()
    if dim ==1: 
        axes [hist.GetXaxis()]
    elif dim ==2: 
        axes = [hist.GetXaxis(), hist.GetYaxis()]
    elif dim ==3: 
        axes = [hist.GetXaxis(), hist.GetYaxis(), hist.GetZaxis()]
    else: 
        axes = [hist.GetAxis(i) for i in range(dim)]
    for ax, axis_name in zip(axes, axis_names):
        ax.SetName(axis_name)


def root_to_template(root_name,
                     file_name,
                     histogram_names=None,
                     metadata={"version": "0.0", "date": datetime.now().strftime('%Y%m%d_%H:%M:%S')}):
    if not HAVE_ROOT:
        raise NotImplementedError("root_to_template requires ROOT, root_numpy")
    froot = rt.TFile(root_name)
    if histogram_names is None: 
        histogram_names = []
        for k in froot.GetListOfKeys():
            if froot.Get(k.GetName()).InheritsFrom("TH1"):
                histogram_names.append(k.GetName())
    _, bins = root_numpy.hist2array(froot.Get(histogram_names[0]), return_edges = True)
    axis_names=get_root_hist_axis_labels(froot.Get(histogram_names[0]))
    histograms = []
    for histogram_name in histogram_names:
        histogram, _ = root_numpy.hist2array(froot.Get(histogram_name), return_edges=True)
        histograms.append(histogram)
    numpy_to_template(bins, histograms, file_name, histogram_names=histogram_names, axis_names=axis_names, metadata=metadata)




def template_to_root(template_name, histogram_names, result_root_name):
    if not HAVE_ROOT:
        raise NotImplementedError("root_to_template requires ROOT, root_numpy")
    raise NotImplementedError()


def combine_templates(templates, histogram_names,
                      result_template_name, result_histogram_name,
                      combination_function=lambda a, b: a+b):
    """
        Function that takes two templates,
        applies the combination_function to them
        and stores them in result_template_name,
        result_histogram_name
    """
    raise NotImplementedError()


def numpy_to_template(bins, histograms, file_name, histogram_names=None, axis_names=None, metadata={"version":"0.0","date":datetime.now().strftime('%Y%m%d_%H:%M:%S')}):

    if histogram_names is None:
        histogram_names = ["{:d}".format(i) for i in range(len(histograms))]
    with h5py.File(file_name, "w") as f:
        print("file f opened, 1st time, ",list(f.keys()))
        for k, i in metadata.items():
            f.attrs[k] = i
        if axis_names is None:
            axis_names = ["" for i in range(len(bins))]
        for i, (b, bn) in enumerate(zip(bins, axis_names)):
            dset = f.create_dataset("bins/{:d}".format(i), data=b)
            dset.attrs["name"] = bn
        for histogram, histogram_name in zip(histograms, histogram_names):
            print("writing histogram name",histogram_name)
            dset = f.create_dataset("templates/{:s}".format(histogram_name), data=histogram)



def template_to_numpy(file_name, histogram_names=None):
    bins = []
    axis_names = []
    histograms = []
    with h5py.File(file_name, "r") as f:
        for i, (k, b) in enumerate(sorted(f["bins"].items())):
            bins.append(np.array(b))
            bn = b.attrs.get("name", "axis{:d}".format(i))
            axis_names.append(bn)

        if histogram_names is None:
            histogram_names = list(f["templates"].keys())
        for histogram_name in histogram_names:
            histograms.append(np.array(f["templates/"+histogram_name]) )
        return bins, histograms, axis_names, histogram_names


def numpy_to_toyfile(file_name, numpy_arrays_and_names, metadata={"version":"0.0","date":datetime.now().strftime('%Y%m%d_%H:%M:%S')}, array_metadatas=None):
    with h5py.File(file_name, "w") as f:
        for k,md in metadata.items(): 
            f.attrs[k]= dumps(md)
        if array_metadatas is None: 
            array_metadatas = [{} for _ in numpy_arrays_and_names]
        for (numpy_array, array_name), array_metadata in zip(numpy_arrays_and_names, array_metadatas):
            ds = f.create_dataset("fits/"+array_name,data=numpy_array, dtype=numpy_array.dtype)
            for k,md in array_metadata.items():
                ds.attrs[k] = dumps(md)




def toyfiles_to_numpy(file_name_pattern, numpy_array_names=None):
    filenames = sorted(glob(file_name_pattern))
    dtype_prototype = None
    results = {}
    for fn in filenames: 
        with h5py.File(fn, "r") as f:
            if numpy_array_names is None: 
                numpy_array_names = list(f["fits"].keys())
                results = {rn:[] for rn in numpy_array_names}
            for i,nan in enumerate(numpy_array_names): 
                res = f["fits/"+nan][()]
                if dtype_prototype is None:
                    dtype_prototype = res.dtype
                assert res.dtype == dtype_prototype
                results[nan].append(res)
    for i,nan in enumerate(numpy_array_names):
        results[nan] = np.concatenate(results[nan])
    return results
