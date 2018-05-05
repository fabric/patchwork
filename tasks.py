from invocations import docs
from invocations.packaging import release
from invocations import travis

from invoke import Collection


ns = Collection(docs, release, travis)
ns.configure({
    'packaging': {
        'sign': True,
        'wheel': True,
        'check_desc': True,
    },
})
