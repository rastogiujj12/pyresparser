# Author: Omkar Pathak

import os
import multiprocessing as mp
import io
import spacy
import pprint
from spacy.matcher import Matcher
from . import utils


class ResumeParser(object):

    def __init__(
        self,
        resume,
        skills_file=None,
        custom_regex=None
    ):
        nlp = spacy.load('en_core_web_sm')
        custom_nlp = spacy.load(os.path.dirname(os.path.abspath(__file__)))
        self.__skills_file = skills_file
        self.__custom_regex = custom_regex
        self.__matcher = Matcher(nlp.vocab)
        self.__details = {
            'name': None,
            'email': None,
            'mobile_number': None,
            'skills': None,
            'college_name': None,
            'degree': None,
            'designation': None,
            'experience': None,
            'company_names': None,
            'no_of_pages': None,
            'total_experience': None,
            'location': None,
        }
        self.__resume = resume
        if not isinstance(self.__resume, io.BytesIO):
            ext = os.path.splitext(self.__resume)[1].split('.')[1]
        else:
            ext = self.__resume.name.split('.')[1]
        self.__text_raw = utils.extract_text(self.__resume, '.' + ext)
        self.__text = ' '.join(self.__text_raw.split())
        self.__nlp = nlp(self.__text)
        self.__custom_nlp = custom_nlp(self.__text_raw)
        self.__noun_chunks = list(self.__nlp.noun_chunks)
        self.__get_basic_details(nlp)
        # print('text raw',self.__text_raw)

    def get_extracted_data(self):
        return self.__details

    def __get_basic_details(self, nlp):
        cust_ent = utils.extract_entities_wih_custom_model(
                            self.__custom_nlp
                        )
        name = utils.extract_name(self.__nlp, matcher=self.__matcher)
        email = utils.extract_email(self.__text)
        mobile = utils.extract_mobile_number(self.__text, self.__custom_regex)
        skills = utils.extract_skills(
                    self.__nlp,
                    self.__noun_chunks,
                    self.__skills_file
                )
        # edu = utils.extract_education(
        #               [sent.string.strip() for sent in self.__nlp.sents]
        #       )
        entities = utils.extract_entity_sections_grad(self.__text_raw)
        location = utils.extract_location(nlp, self.__matcher, self.__text_raw)
        # extract name
        try:
            self.__details['name'] = cust_ent['Name'][0]
        except (IndexError, KeyError):
            self.__details['name'] = name

        # extract email
        self.__details['email'] = email

        # extract mobile number
        self.__details['mobile_number'] = mobile

        # extract skills
        self.__details['skills'] = skills

        #extract location
        self.__details['location'] = location

        # extract college name
        try:
            self.__details['college_name'] = entities['College Name']
        except KeyError:
            pass

        # extract education Degree
        try:
            self.__details['degree'] = cust_ent['Degree']
        except KeyError:
            pass

        # extract designation
        try:
            self.__details['designation'] = cust_ent['Designation']
        except KeyError:
            pass

        # extract company names
        try:
            self.__details['company_names'] = cust_ent['Companies worked at']
        except KeyError:
            pass

        try:
            self.__details['experience'] = entities['experience']
            try:
                exp = round(
                    utils.get_total_experience(entities['experience']) / 12,
                    2
                )
                self.__details['total_experience'] = exp
            except KeyError:
                self.__details['total_experience'] = 0
        except KeyError:
            self.__details['total_experience'] = 0
        self.__details['no_of_pages'] = utils.get_number_of_pages(
                                            self.__resume
                                        )
        return


def resume_result_wrapper(resume):
    parser = ResumeParser(resume)
    return parser.get_extracted_data()


if __name__ == '__main__':
    pool = mp.Pool(mp.cpu_count())

    resumes = []
    data = []
    for root, directories, filenames in os.walk('resumes'):
        for filename in filenames:
            file = os.path.join(root, filename)
            resumes.append(file)

    results = [
        pool.apply_async(
            resume_result_wrapper,
            args=(x,)
        ) for x in resumes
    ]

    results = [p.get() for p in results]

    pprint.pprint(results)

#input_candidate = '{"__v":{"521":0},"_id":{"521":{"$oid":"5d3eb1d26f13a2479c2e163c"}},"achievements":{"521":[{"_id":{"$oid":"5d3f0eba6f13a2479c2e16ba"},"description":"business Strategy and branding Competition at Amity Global Business School","position":"First","level":"National","institution":"AMITY BUSINESS SCHOOL","year":{"$date":"2019-02-01T15:20:26.643Z"},"event":"BRAND SAMVAD"},{"_id":{"$oid":"5d3f0ed66f13a2479c2e16bb"},"position":"Third","level":"National","institution":"SSEC BHAVNAGAR","year":{"$date":"2017-02-01T15:20:54.824Z"},"event":"GOOGLE MASTER"}]},"certification":{"521":[{"_id":{"$oid":"5d3f0dcf6f13a2479c2e16b4"},"link":"https:\\/\\/drive.google.com\\/file\\/d\\/1wXfaQXa6CVXZOYRXTzU1mpaOO90goq2P\\/view","score":92,"completedOn":{"$date":"2019-07-20T00:00:00.000Z"},"course":"Social and Community Manager","institution":"ONLINE BUSINESS ORGANIZATION"},{"_id":{"$oid":"5d3f0e0b6f13a2479c2e16b5"},"link":"https:\\/\\/drive.google.com\\/file\\/d\\/0B7Q0eJO5hXBnaVRjakRJR0F6Vm8\\/view","score":90,"completedOn":{"$date":"2017-07-18T00:00:00.000Z"},"course":"FUNDAMENTALS OF DIGITAL MARKETING","institution":"GOOGLE"},{"_id":{"$oid":"5d3f0e7d6f13a2479c2e16b9"},"link":"https:\\/\\/drive.google.com\\/file\\/d\\/1LbUQOd-eSzm2_d17uhIKbpKbTGUAPvxf\\/view","score":82,"completedOn":{"$date":"2019-07-15T00:00:00.000Z"},"course":"GOOGLE ANALYTICS FOR BEGINEERS","institution":"GOOGLE"}]},"college":{"521":null},"collegeAddress":{"521":null},"collegeWebsite":{"521":null},"companyName":{"521":null},"companySize":{"521":null},"courses":{"521":[]},"createdAt":{"521":{"$date":"2019-07-29T08:44:02.276Z"}},"dateOfBirth":{"521":{"$date":"1995-08-24T00:00:00.000Z"}},"description":{"521":null},"education":{"521":[{"_id":{"$oid":"5d3f0b576f13a2479c2e16a3"},"otherCollege":"St Thomas Highschool","levelOfStudy":"10th","totalScore":"100","score":88.31,"institution":{"$oid":"5d322190a3fb52550485f19f"},"course":{"$oid":"5d328536a3fb52550485f1a5"},"to":{"$date":"2010-01-01T00:00:00.000Z"},"from":{"$date":"2009-01-01T00:00:00.000Z"}},{"_id":{"$oid":"5d3f0b976f13a2479c2e16a4"},"otherCollege":"SARASWATI HIGHER SECONDARY SCHOOL","levelOfStudy":"12th","totalScore":"100","score":64,"description":"PCM MARKS","institution":{"$oid":"5d322190a3fb52550485f19f"},"course":{"$oid":"5d328536a3fb52550485f1a5"},"to":{"$date":"2012-01-01T00:00:00.000Z"},"from":{"$date":"2011-01-01T00:00:00.000Z"}},{"_id":{"$oid":"5d3f0bff6f13a2479c2e16a6"},"otherCollege":"GUJARAT TECHNOLOGICAL UNIVERSITY","levelOfStudy":"Undergraduate","totalScore":"100","score":70,"description":"CGPI 7.55","institution":{"$oid":"5d322190a3fb52550485f19f"},"course":{"$oid":"5d321ed3a3fb52550485eea0"},"to":{"$date":"2016-01-01T00:00:00.000Z"},"from":{"$date":"2012-01-01T00:00:00.000Z"}},{"_id":{"$oid":"5d3f0c476f13a2479c2e16a9"},"otherCollege":"GUJARAT UNIVERSITY","levelOfStudy":"Postgraduate","totalScore":"5","score":3.9,"description":"GRADE SYSTEM OF 5 ","institution":{"$oid":"5d322190a3fb52550485f19f"},"course":{"$oid":"5d321ed3a3fb52550485f022"},"to":{"$date":"2020-01-01T00:00:00.000Z"},"from":{"$date":"2018-01-01T00:00:00.000Z"}}]},"email":{"521":"hardik.ft20@bkschool.org.in"},"interests":{"521":null},"isActive":{"521":true},"isAdmin":{"521":false},"isCollegeMapped":{"521":null},"isDeleted":{"521":false},"isEmailVerified":{"521":true},"isOnBoardingComplete":{"521":true},"location":{"521":"Ahmedabad"},"mobile":{"521":"8160385344"},"name":{"521":{"first":"Hardik","last":"Vaghela"}},"nationality":{"521":null},"numberOfStudents":{"521":null},"otp":{"521":"443043"},"password":{"521":"$2a$10$Ce7axf9x\\/rSsnu0fL3DNQe2FiLDiu6pq6aB1Yp90stPOuuPY3yUaG"},"placementReports":{"521":null},"positions":{"521":[{"_id":{"$oid":"5d3f0fee6f13a2479c2e16bf"},"present":true,"from":{"$date":"2018-08-01T15:25:34.764Z"},"description":"WORKING AS A STUDENT PLACEMENT COORDINATOR OF PLACEMENT COMMITTEE TO HANDLE CORPORATE AND EDUCATIONAL CONNECTIONS.","type":"LeaderShip","institution":"BK SCHOOL OF BUSINESS MANAGEMENT","position":"STUDENT PLACEMENT COORDINATOR","society":"PLACEMENT COMMITTEE"}]},"profilePicture":{"521":"https:\\/\\/perspectico-uploads.s3.amazonaws.com\\/profileImage\\/1564389981image.jpeg"},"projects":{"521":[{"_id":{"$oid":"5d3f0f156f13a2479c2e16bc"},"present":false,"to":{"$date":"2019-05-01T15:21:58.004Z"},"from":{"$date":"2019-01-01T15:21:58.002Z"},"team":"Team","description":"\\u00e2\\u20ac\\u00a2 Integral member in team project which deals with the market research about organic and milk products.\\n\\u00e2\\u20ac\\u00a2 Conducted market survey, area mapping and met various consumers to know their perception.\\n","title":"Consumer Perception towards organic products by IIM Ahmedabad","organization":"ARE INFOTECH AND IIM AHMEDABAD"},{"_id":{"$oid":"5d3f0f4a6f13a2479c2e16bd"},"present":false,"to":{"$date":"2016-05-01T15:22:51.291Z"},"from":{"$date":"2015-05-01T15:22:51.289Z"},"team":"Team","description":"Integral member in team project to develop an app on giving lifts to people who travel solo.\\nDesigned UI and worked on backhand of the project.","title":"LIFT? YA!","organization":"JNEXT DEVELOPMENT "},{"_id":{"$oid":"5d3f0f8e6f13a2479c2e16be"},"present":false,"to":{"$date":"2017-08-01T15:23:58.864Z"},"from":{"$date":"2017-05-01T15:23:58.862Z"},"team":"Team","description":"\\u00e2\\u20ac\\u00a2 Team head of an android app for the people who wants to track their business growth and information.\\n\\u00e2\\u20ac\\u00a2 Troubleshooting and adding modules.","title":"EASYBRM","organization":"AELIYA INFOTECH PVT LTD"}]},"resume":{"521":[{"_id":{"$oid":"5d3f0b016f13a2479c2e16a0"},"url":"https:\\/\\/perspectico-uploads.s3.ap-south-1.amazonaws.com\\/resumes\\/1564412672resume.pdf"}]},"score":{"521":48.75},"slug":{"521":"5d3eb1d26f13a2479c2e163c"},"testingUserId":{"521":"5d3eb25e82a5f55d1d3373e5"},"type":{"521":"STUDENT"},"university":{"521":null},"updatedAt":{"521":{"$date":"2019-07-29T08:44:02.276Z"}},"videoPitch":{"521":[]},"website":{"521":null},"work":{"521":[{"_id":{"$oid":"5d3f0ce06f13a2479c2e16ae"},"present":false,"to":{"$date":"2019-07-01T15:12:33.058Z"},"from":{"$date":"2019-05-01T15:12:33.058Z"},"company":"ARE INFOTECH","description":"Worked on 24 different projects as summer intern\\nHandled all social media and advertising activities including content creation\\nauditing and monitoring","type":"Internship","position":"SOCIAL MEDIA INTERN "},{"_id":{"$oid":"5d3f0ccd6f13a2479c2e16ad"},"present":false,"to":{"$date":"2017-08-01T15:12:13.666Z"},"from":{"$date":"2017-05-01T15:12:13.665Z"},"company":"AELIYA INFOTECH PVT LTD","description":"\\u00ef\\u201a\\u00b7 Worked as a General Manager and Android App Department Manager\\n\\u00ef\\u201a\\u00b7 Mentored trainee for the app development\\n\\u00ef\\u201a\\u00b7 Focused on building android apps and troubleshooting as well as hr activities","type":"Full-Time","position":"PROJECT MANAGER"},{"_id":{"$oid":"5d3f0d236f13a2479c2e16b1"},"present":false,"to":{"$date":"2016-05-01T15:13:40.135Z"},"from":{"$date":"2015-05-01T15:13:40.131Z"},"company":"JNEXT DEVELOPMENT PVT LTD","description":"\\u00ef\\u201a\\u00b7 Worked as an intern for developing an android app\\n\\u00ef\\u201a\\u00b7 Learned android app building and java.","type":"Internship","position":"ANDROID AND JAVA INTERN"},{"_id":{"$oid":"5d3f0d6c6f13a2479c2e16b3"},"present":false,"to":{"$date":"2017-08-01T15:14:52.489Z"},"from":{"$date":"2017-07-01T15:14:52.488Z"},"company":"WHITE PANDA ","description":"VIRTUAL INTERNSHIP BASED ON CONTENT DEVELOPMENT AND CONTENT WRITING ","type":"Internship","position":"WRITING INTERN"}]}}'
