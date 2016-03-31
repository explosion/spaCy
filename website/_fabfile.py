from __future__ import print_function

from fabric.api import local
import os
import hashlib
import mimetypes
import shutil

import boto.s3.connection


mimetypes.init()

buckets = {
    'staging': 'staging.spacy.io',
    'production': 'spacy.io',
}


def compile():
    shutil.rmtree('www')
    local('NODE_ENV=s3 harp compile')


def publish(env='staging', site_path='www'):
    os.environ['S3_USE_SIGV4'] = 'True'
    conn = boto.s3.connection.S3Connection(host='s3.eu-central-1.amazonaws.com',
        calling_format=boto.s3.connection.OrdinaryCallingFormat())
    bucket = conn.get_bucket(buckets[env], validate=False)

    keys = {k.name: k for k in bucket.list()}
    keys_left = set(keys)

    for root, dirnames, filenames in os.walk(site_path):
        for dirname in dirnames:
            target = os.path.relpath(os.path.join(root, dirname), site_path)
            source = os.path.join(target, 'index.html')

            if os.path.exists(os.path.join(root, dirname, 'index.html')):
                redirect = '//%s/%s' % (bucket.name, target)
                key = bucket.lookup(source)
                if not key:
                    key = bucket.new_key(source)
                    key.set_redirect(redirect)
                    print('setting redirect for %s' % target)
                elif key.get_redirect() != redirect:
                    key.set_redirect(redirect)
                    print('setting redirect for %s' % target)

                if source in keys_left:
                    keys_left.remove(source)

        for filename in filenames:
            source = os.path.join(root, filename)

            if filename == 'index.html':
                target = os.path.normpath(os.path.relpath(root, site_path))
                if target == '.':
                    target = filename
            else:
                target = os.path.normpath(os.path.join(os.path.relpath(root, site_path), filename))
                if target.endswith('.html'):
                    target = target[:-len('.html')]

            content_type = mimetypes.guess_type(source)[0]
            cache_control = 'no-transform,public,max-age=300,s-maxage=300'
            checksum = hashlib.md5(open(source).read()).hexdigest()

            if (target not in keys
                or keys[target].etag.replace('"', '') != checksum):

                key = bucket.new_key(target)
                if content_type:
                    key.content_type = content_type
                key.set_contents_from_filename(source,
                    headers={'Cache-Control': cache_control})
                print('uploading %s' % target)

            elif content_type:
                key = bucket.lookup(target)
                if (key
                    and (key.content_type != content_type
                         or key.cache_control != cache_control)):
                    key.copy(key.bucket, key.name, preserve_acl=True,
                        metadata={'Content-Type': content_type,
                                  'Cache-Control': cache_control})
                    print('update headers %s' % target)

            if target in keys_left:
                keys_left.remove(target)

    for key_name in keys_left:
        print('deleting %s' % key_name)
        bucket.delete_key(key_name)
