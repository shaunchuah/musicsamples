# SampleTrek

Open source lab sample inventory tracking system and electronic lab notebook created with Django (Python web framework) to support clinical research in Scotland.

## Goals

Help lab researchers improve time to discovery and reduce time spent on logistics by providing tooling to manage a large amount of samples

<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary><h2 style="display: inline-block">Table of Contents</h2></summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#deployment">Deployment</a></li>
    <li><a href="#usage">Usage</a></li>
    <!--<li><a href="#roadmap">Roadmap</a></li>-->
    <li><a href="#customisation">Customisation</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#author">Author</a></li>
    <li><a href="#acknowledgements">Acknowledgements</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->
## About The Project

### Tracking of 30,000 research samples across multiple sites and labs
SampleTrek was developed to solve the problem of tracking 30,000 research samples across multiple study sites with multiple laboratory endpoints. In our use we deployed it on a single droplet/virtual private server hosted by DigitalOcean and used Amazon Web Services for handling email and database backups. Code was deployed using github and this allowed rapid deployment of new features as the need arose. Check out the study here: [MUSIC IBD Study](https://www.musicstudy.uk)

### QR code labelling
Cryogenic QR code labels were bulk printed from a label printing company and research samples were tagged at the point of collection and registered onto SampleTrek. At specified receiving entrypoints to various lab workflows the samples were scanned in bulk to update their location (alternatively a status could be set into the location eg. "Departure Glasgow").

### Electronic lab notebook with sample tagging
A mini electronic lab notebook was created which allows tagging of samples used in order to facilitate collaboration and to allow easy finding of relevant data pertaining to experiments carried out on the samples.


### Built With

* [Django](https://www.djangoproject.com/)
* [Postgres](https://www.postgresql.org/)
* [UI kit from Creative Tim - includes Bootstrap/JQuery](https://www.creative-tim.com/product/black-dashboard-django)

<!-- GETTING STARTED -->
## Getting Started

To get a local copy up and running follow these simple steps. The default .env file will set up Django to run using sqlite as the backend.

This requires a level of comfort and familiarity with python/django/linux/postgres web deployment. If you run into difficulty, you could consider hiring a django full stack developer to help. We had a hard look at available commercial LIMS systems and due to various reasons they were found to be lacking (data not located in UK, pricey, hard to customise and adapt to changing experimental workflows).

### Prerequisites

* Python > 3.7.2
* Pip

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/shaunchuah/sampletrek.git
   ```
2. Django setup
   ```sh
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver
   ```

### Notes

Sample tagging to notes does not work unless you configure the cache settings. Works in production using redis. You could try installing redis on your development environment.

## Deployment

You will need a domain name to deploy on. Configure the domain to point at your server.

### Suggested Server Software Requirements:

* Ubuntu 20.04
* Python
* Postgres
* Nginx
* Gunicorn
* Redis

Suggested production deployment:

1. Ubuntu VPS instance (DigitalOcean, Linode, Lightsail etc. many options) - we used 20.04 LTS on DigitalOcean
2. Install python, postgres into your VPS and set it up (alternatively connecting to a managed database service might be easier although more costly)
3. Setup nginx and gunicorn (static requests through nginx, dynamic requests redirected to gunicorn serving Django). [Useful guide here](https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-18-04).
4. Set up an account on AWS for password reset emails or an alternative email provider of your choice
5. Set up redis for caching (required for sample tagging to work properly - [https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-redis-on-ubuntu-20-04](https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-redis-on-ubuntu-20-04))
5. Clone the repo into a folder of your choice and remember to run:

    ```sh
    pip install -r requirements.txt
    python manage.py migrate
    python manage.py collectstatic
    ```
6. **Edit .env file to a production configuration**
7. Start up the whole stack and it should hopefully be working!
8. Now that it's working - setup SSL encryption on your server using letsencrypt
9. Harden your production .env file





<!-- USAGE EXAMPLES -->
## Usage

Use this space to show useful examples of how a project can be used. Additional screenshots, code examples and demos work well in this space. You may also link to more resources.



<!-- Customisation -->
## Customisation

### Project Architecture Overview

* app: main application logic
* authentication: all authentication handling/views here
* core: settings.py and templates/css/js lives here
* media: local media folder for development
* staticfiles: local staticfiles folder

### Customisation Tips 

Here are some tips for customising this to suit your workflow:
* The main logic sits in the app folder
* Modify the main model in app/models.py - add fields that you want to QC on - think of it like an excel spreadsheet with column headers that you specify here
* If you do alter the model - you may wish to alter: 
1. SampleForm in app/forms.py
2. export_excel function in views.py
3. sample-detail.html in core/templates
* Dropdown select fields are configured in app/forms.py
* Most of the view logic is in app/views.py. I have written this mostly in function based views to make it explicit and easy to identify where you wish to alter the workflow rather than class based views. I appreciated this means the views.py file is more verbose but hopefully this helps you customise this to fit what you're trying to achieve.
* The templates are found in core/templates. Most functions are using a single template for a single view so you can customise particular aspects as you desire

<!-- ROADMAP 
## Roadmap

See the [open issues](https://github.com/github_username/repo_name/issues) for a list of proposed features (and known issues).

-->

<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Possible areas of development

1. Make deployment easier for beginners/non-technical users - perhaps Docker? (I'm afraid I don't have time to learn that)
2. Improving testing coverage
3. Perhaps simplifying the dependency list
4. Improving the note writing interface
5. Clean up CSS and javascript static files while allowing easy customisation

## Code of Conduct

Code of conduct available [here].(docs/code_of_conduct.md) taken from [https://www.contributor-covenant.org/](https://www.contributor-covenant.org/).

<!-- LICENSE -->
## License

Distributed under the MIT License.

MIT License

Copyright (c) 2021 Shaun Chuah.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


<!-- ACKNOWLEDGEMENTS -->
## Acknowledgements

* [Creative Tim for the initial UI template](https://www.creative-tim.com/product/black-dashboard-django)
* [Django](https://www.djangoproject.com/)
* [Postgres](https://www.postgresql.org/)
* [Django Ckeditor](https://github.com/django-ckeditor/django-ckeditor)
* [Django Storages](https://django-storages.readthedocs.io/en/latest/)
* [Django Rest Framework](https://www.django-rest-framework.org/)
* [Django Taggit](https://django-taggit.readthedocs.io/en/latest/)
* [Django Select2](https://django-select2.readthedocs.io/en/latest/)
* [Django Filter](https://django-filter.readthedocs.io/en/master/)
* [Django Simple History](https://django-simple-history.readthedocs.io/en/latest/)
* [Django Widget Tweaks](https://pypi.org/project/django-widget-tweaks/)
* [Open Pyxl](https://openpyxl.readthedocs.io/en/stable/)
* [D3.js](https://d3js.org/)

<!-- CONTACT -->
## Author

Dr Shaun Chuah <br />
Clinical Research Fellow in Gastroenterology <br />
Centre for Inflammation Research<br />
Queen's Medical Research Institute <br />
University of Edinburgh

## Contact

If you've used this to create something cool let me know about it!

Twitter: [@chershiong](https://twitter.com/chershiong) <br />
Email: cchuah@ed.ac.uk <br />
Project Link: [https://github.com/shaunchuah/sampletrek](https://github.com/shaunchuah/sampletrek)

## Disclaimer

This was written over 2-3 weeks with the aim of rapid deployment so there are imperfections eg no unit testing. Testing was done in real life as this was not mission critical and a degree of failure could be tolerated and fixed.


<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/shaunchuah/repo.svg?style=for-the-badge
[contributors-url]: https://github.com/shaunchuah/repo/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/github_username/repo.svg?style=for-the-badge
[forks-url]: https://github.com/shaunchuah/repo/network/members
[stars-shield]: https://img.shields.io/github/stars/github_username/repo.svg?style=for-the-badge
[stars-url]: https://github.com/shaunchuah/repo/stargazers
[issues-shield]: https://img.shields.io/github/issues/github_username/repo.svg?style=for-the-badge
[issues-url]: https://github.com/shaunchuah/repo/issues
[license-shield]: https://img.shields.io/github/license/github_username/repo.svg?style=for-the-badge
[license-url]: https://github.com/shaunchuah/repo/blob/master/LICENSE.txt