"""
Wrapper for Fast Holographic Deconvolution (FHD).

"""
import re
from glob import glob
from multiprocessing import Pool

import pidly


class FHDRun(object):
    """
    Base wrapper object for FHD command.

    """
    def __init__(self, command, *args, **kwargs):
        self.command = command
        self.idl_path = 'idl'
        if args:
            self.command_type = 'func'
            self.args = args
            if kwargs:
                self.kwargs = kwargs
            else:
                self.kwargs = dict()
        elif kwargs:
            self.command_type = 'pro'
            self.kwargs = kwargs
            self.args = tuple()
        self.result = None

    def set_args(self, *args):
        self.args = args

    def set_kwargs(self, **kwargs):
        for k, v in kwargs.items():
            if isinstance(v, bool):
                v = int(v)
            self.kwargs[k] = v

    def run(self):
        if self.command_type == 'pro':
            call_pro(self.command, idl_path=self.idl_path, **self.kwargs)
        elif self.command_type == 'func':
            self.result = call_func(self.command, idl_path=self.idl_path,
                                    *self.args, **self.kwargs)


class GeneralObs(FHDRun):
    """
    Wrapper object for FHD general_obs.

    """
    def __init__(self, uvfits, kwargs, idl_path='idl'):
        """
        Parameters
        ----------
        uvfits: string or array-like
            If string, full path to uvfits files. If the string contains
            wildcard character "*?[]", `glob` will be used to search for files.
            If array-like, each element is a full path to a uvfits file.
        kwargs: dict
            Keyward parameters for general_obs
        idl_path: str, optional
            A full path to IDL. IDL session will be opened from this path.

        """
        super(GeneralObs, self).__init__('general_obs', **kwargs)
        self.load_uvfits(uvfits)
        self.idl_path = idl_path

    def load_uvfits(self, uvfits):
        """
        Load uvfits from files.

        Parameters
        ----------
        uvfits: string or array-like
            If string, full path to uvfits files. If the string contains
            wildcard character "*?[]", `glob` will be used to search for files.
            If array-like, each element is a full path to a uvfits file.

        """
        if isinstance(uvfits, str):
            if re.search('[*?\[\]]', uvfits) is not None:
                self.kwargs['vis_file_list'] = glob(uvfits)
            else:
                self.kwargs['vis_file_list'] = [uvfits, ]
        else:
            self.kwargs['vis_file_list'] = uvfits


class ParGeneralObs(GeneralObs):
    """
    Parallel version of GeneralObs.

    This object take a list of uvifts
    """


def call_func(func_name, idl_path='idl', *func_args, **func_kwargs):
    idl = pidly.IDL(idl_path)
    result = idl.func(func_name, *func_args, **func_kwargs)
    idl.close()
    return result

def call_pro(pro_name, idl_path='idl', **pro_kwargs):
    idl = pidly.IDL(idl_path)
    idl.pro(pro_name, **pro_kwargs)
    idl.close()
