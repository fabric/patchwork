from invocations import docs, travis
from invocations.packaging import release
from invocations.pytest import test

from invoke import Collection


ns = Collection(docs, release, travis, test)
ns.configure({
    'packaging': {
        'sign': True,
        'wheel': True,
        'check_desc': True,
    },
})
