import sys
import os
from collections import OrderedDict
import re
import urlparse
import argparse

ref_suffixes = ["_ref", "-ref"]

class ManifestError(Exception):
    pass

class Manifest(object):
    test_types = ["testharness", "reftest", "manual", "helper"]

    def __init__(self, root_path, path):
        self.root_path = root_path
        self.path = path
        self.data = OrderedDict()
        for test_type in self.test_types:
            self.data[test_type] = []

    @classmethod
    def from_file(cls, root_path, path):
        try:
            with open(path) as f:
                data = f.read()
                return cls.from_string(root_path, path, data)
        except IOError:
            with open(path, "w") as f:
                return cls(root_path, path)

    @classmethod
    def from_string(cls, root_path, path, data):
        header_re = re.compile("^\[(.*)\]\s*$")

        headers_seen = set()
        current_header = None

        rv = cls(root_path, path)

        for line in data.split("\n"):
            line = line.strip()
            if not line:
                continue

            header_match = header_re.match(line)
            if header_match:
                header = header_match.groups()[0]
                if header in cls.test_types:
                    if header not in headers_seen:
                        current_header = header
                    else:
                        raise ManifestError("Multiple instances of header %s" % header)
                else:
                    raise ManifestError("Unknown header %s" % header)
                headers_seen.add(header)
            else:
                if not current_header:
                    raise ManifestError("Found data before first header")
                items = line.split()
                items.reverse()
                url = items.pop()
                data = {}

                if current_header == "reftest":
                    if len(items) < 2:
                        raise ManifestError("Reftest needs test url, reference type and reference url")
                    ref_type = items.pop()
                    if ref_type not in ["==", "!="]:
                        raise ManifestError("Invalid reference type %s" % ref_type)
                    data["ref_type"] = ref_type
                    data["ref_url"] = items.pop()

                for item in items:
                    assert " " not in line, line
                    key, value = item.split(":", 1)
                    if key in data:
                        raise ManifestError("Duplicate key %s" % key)
                    else:
                        data[key] = value

                rv.add(current_header, url, data)

        return rv

    def __len__(self):
        return reduce(lambda x,y:x+y, map(len, self.data.items()), 0)

    def contains_path(self, path):
        for test_type, items in self.data.iteritems():
            for item in items:
                if (item["url"].split("?", 1)[0] == path or
                    (test_type == "reftest" and
                     item["ref_url"].split("?", 1)[0] == path)):
                    return True
        return False

    def add(self, test_type, url, props=None):
        test_data = {"url": url}
        if props:
            test_data.update(props)
        self.data[test_type].append(test_data)

    def write(self):
        with open(self.path, "w") as f:
            for header, items in self.data.iteritems():
                f.write("[%s]\n" % header)
                for item in items:
                    if header == "reftest":
                        pos_keys = ["url", "ref_type", "ref_url"]
                    else:
                        pos_keys = ["url"]
                    first_key = True
                    for pos_key in pos_keys:
                        if not first_key:
                            f.write(" ")
                        else:
                            first_key = False
                        f.write(item[pos_key])
                    others = [key for key in item if key not in pos_keys]
                    for key in others:
                        f.write(" %s:%s" % (key, item[key]))
                    f.write("\n")
                f.write("\n")

    def iter_type(self, test_type):
        for item in self.data[test_type]:
            yield item

    @property
    def server_path(self):
        #This isn't correct cross-platform
        rel_path = os.path.relpath(os.path.split(self.path)[0], self.root_path)
        assert ".." not in rel_path, rel_path
        if rel_path.startswith("."):
            rel_path = rel_path[1:]
        url = rel_path.replace(os.path.sep, "/")
        return "/" + url

def get_ref(path):
    base_path, filename = os.path.split(path)
    name, ext = os.path.splitext(filename)
    for suffix in ref_suffixes:
        possible_ref = os.path.join(base_path, name + suffix + ext)
        if os.path.exists(possible_ref):
            return possible_ref

def guess_type(path):
    #This should actually parse the file and extract the metadata
    if not os.path.exists(path):
        raise IOError("%s does not exist" % path)

    base_path, filename = os.path.split(path)
    name, ext = os.path.splitext(filename)
    if filename == "MANIFEST" or filename.startswith("."):
        return None

    if filename.lower().endswith("-manual"):
        return "manual"

    if get_ref(path):
        return "reftest"

    if ext in [".html", ".htm", ".xhtml", ".xht", ".svg"]:
        testharness_re = re.compile("<script\\s*src=[\"']?/resources/testharness.js[\"']?")
        php_re =re.compile("\.php")
        with open(path) as f:
            text = f.read()
            if php_re.findall(text):
                return None
            if testharness_re.findall(text):
                return "testharness"

    return "helper"

def update_manifests(root_path, dir_walker):
    blacklist = ["", "tools", "resources", "common"]
    for dirpath, dirnames, filenames in dir_walker:
        if filenames:
            manifest = update_manifest(root_path, dirpath, filenames)
        if len(manifest):
            manifest.write()

def update_manifest(root_path, path, filenames):
    manifest = Manifest.from_file(root_path, os.path.join(path, "MANIFEST"))
    for filename in filenames:
        if os.path.isdir(filename):
            continue

        if not manifest.contains_path(filename):
            test_type = guess_type(os.path.join(path, filename))
            if test_type is None:
                continue
            if test_type == "reftest":
                props = {"ref_type": "==",
                         "ref_url": os.path.relpath(get_ref(os.path.join(path, filename)),
                                                    path)}
            else:
                props = None
            manifest.add(test_type, filename, props)
    return manifest

def abs_path(path):
    return os.path.abspath(path)

def parse_args():
    parser = argparse.ArgumentParser(description="Runner for web-platform-tests tests.")
    parser.add_argument("tests_path", action="store", type=abs_path,
                        help="Path to web-platform-tests")
    parser.add_argument("--update-root", action="store", type=abs_path,
                        help="Path to start the update")
    parser.add_argument("--no-recurse", action="store_true",
                        help="Don't recurse into subdirectories")
    return parser.parse_args()

def main():
    args = parse_args()
    if not args.update_root:
        args.update_root = args.tests_path

    if args.no_recurse:
        def one_dir_walker():
            yield (args.update_root, [],
                   [item for item in os.listdir(path) if not os.path.isdir(item)])
        walker = one_dir_walker()
    else:
        walker = os.walk(args.tests_path)

    update_manifests(args.tests_path, walker)

if __name__ == "__main__":
    main()
