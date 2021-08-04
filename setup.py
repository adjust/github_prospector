from setuptools import setup


setup(
    name='github_prospector',
    version='0.1',
    packages=['github_prospector', 'github_prospector.metrics'],
    url='https://github.com/adjust/github_prospector',
    license='',
    author='Maxim Kuznetsov',
    author_email='maksim.kuznetsov@akvelon.com',
    description='CLII analytic tool for GitHub\'s teams, repositories, users.',
    install_requires=['PyGithub==1.55']
)
