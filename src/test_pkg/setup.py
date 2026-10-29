from setuptools import setup

package_name = 'test_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='mi',
    maintainer_email='11565806+tong-boming@user.noreply.gitee.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'helloworld=test_pkg.node_helloworld:main',
            'test=test_pkg.test:main',
            'helloworld_pub=test_pkg.topic_helloworld_pub:main',
            'helloworld_sub=test_pkg.topic_helloworld_sub:main',
            'topic_motion=test_pkg.topic_motion:main',
        ],
    },
)
