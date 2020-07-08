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
        str hist_name: name of template, if None, return a dict 
        indexed by histogram names containing the histograms
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
        if hist_name is None:
            ret = dict()
            for hist_name in f["templates"]:
                h = mh.Histdd(bins=bins, axis_names=bin_names)
                h.histogram = np.array(f["templates/"+hist_name])
                ret[hist_name] = h
        else:
            ret = mh.Histdd(bins=bins, axis_names=bin_names)
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

def dict_to_structured_array(d):
    """
        Function that reads a dict and transforms it to a structured numpy array of length 1
        input: 
        d-- dict 
        output: 
        structured array with names equal to sorted(keys of d), and values equal to the values
    """
    dtype = [(k,type(i)) for k,i in sorted(d.items())]
    ret = np.array([tuple(i for k,i in sorted(d.items()))], dtype=dtype)
    return ret

def structured_array_to_dict(sa):
    ret = {n:sa[n][0] for n in sa.dtype.names}
    return ret


def toydata_to_file(file_name, datasets_array, dataset_names, overwrite_existing_file=True,
                    metadata={"version":"0.0","date":datetime.now().strftime('%Y%m%d_%H:%M:%S')} ):   
    """
        Function to store toy data (in the form of numpy structured arrays) in a hdf5 file

        datasets_array: list of list of datasets. (So each element is a list of datasets-- calibration, science, ancillary) 
        dataset_names: list of the names of each dataset (so e.g. data_sci, data_cal, data_anc) toyMC true generator parameters may also be stored this way. 
        if overwrite_existing_file is true, a new file is created overwriting the old, otherwise, the file is created if absent and appended to otherwise. 
    """
    if overwrite_existing_file or not path.exists(file_name):
        mode = "w"
    else:
        mode = "a"
    n_datasets = len(datasets_array)
    n_datasets_prev = 0 
    with h5py.File(file_name, mode) as f: 
        if mode=="a":
            n_datasets_prev = loads(f.attrs["n_datasets"])
            assert dataset_names == loads(f.attrs["dataset_names"]) #otherwise the saving underneath will go wrong
        f.attrs["n_datasets"] = dumps(n_datasets+n_datasets_prev)
        f.attrs["dataset_names"] = dumps(dataset_names)
        for k,i in metadata.items():
            f.attrs[k] = i
        
        for i in range(n_datasets):
            for j, (dataset, dataset_name) in enumerate(zip(datasets_array[i],dataset_names)):
                f.create_dataset("{:d}/{:s}".format(i+n_datasets_prev,dataset_name), data=dataset)

def toydata_from_file(file_name,datasets_to_load=None):
    """
        function to load toy data from file to array of structured numpy arrays. For error-checking, the name structure of the datasets is also included
    """
    datasets_array = []
    with h5py.File(file_name,"r") as f: 
        dataset_names = loads(f.attrs["dataset_names"])
        n_datasets = loads(f.attrs["n_datasets"])
        if datasets_to_load is None:
            dataset_iterator = range(n_datasets)
        else:
            dataset_iterator = datasets_to_load
        for i in dataset_iterator:
            dataset_array = []
            for dataset_name in dataset_names:
                dataset_array.append(f["{:d}/{:s}".format(i,dataset_name)][()])
            datasets_array.append(dataset_array)
    
    return datasets_array, dataset_names


def process_templates(template_files, file_name, 
                      histogram_handler= lambda hs:sum(hs)):
    """
        Function that reads in a list of templates. 
        For each histogram name, histogram_handler will be called 
        on the array of the histograms with that name
        The example function, for example, would add together histograms with the same name. 
        str template_files : list of names of input template files
        str file_name name of output file
        function histogram_handler: function that takes a list of multihists and returns a multihist. 
    """
    histogram_dict = dict()
    for template_file in template_files: 
        histograms = template_to_multihist(template_file, hist_name=None)
        for n,h in histograms.items():
            if n not in histogram_dict:
                histogram_dict[n] = []
            histogram_dict[n].append(h)
            
    histogram_names = []
    histograms = []
    for n, hs in histogram_dict.items():
        histogram_names.append(n)
        histograms.append(histogram_handler(hs) )
    multihist_to_template(histograms, file_name, histogram_names)

