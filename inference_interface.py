import numpy as np
import h5py

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
    f = h5py.File(file_name, "r")
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


def multihist_to_template(histograms, histogram_names=None):
    if not HAVE_MULTIHIST:
        raise NotImplementedError("template_to_multihist requires multihist")
    raise NotImplementedError()


def root_to_template(root_name, histogram_names=None):
    if not HAVE_ROOT:
        raise NotImplementedError("root_to_template requires ROOT, root_numpy")
    raise NotImplementedError()


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




def numpy_to_template(bins, histograms, histogram_names=None, axis_names=None):
    raise NotImplementedError()
