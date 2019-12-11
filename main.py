import bs4
from typing import List
import re


class GenericSkill:
    def __init__(self, skill_content: str):
        self.skill_name = skill_content.split('.', 1)[0]
        self.skill_description = skill_content.split('.', 1)[1]
        last_open_paran = self.skill_description.rfind('(')
        self.skill_description = self.skill_description[:last_open_paran]

    def __repr__(self):
        return f"{self.skill_name}. {self.skill_description}"


class SkillLevel(GenericSkill):
    def __init__(self, skill_content):
        super().__init__(skill_content)
        last_open_paran = skill_content.rfind('(')
        self.level = skill_content[last_open_paran:]

    def __repr__(self):
        return f"{super().__repr__()} {self.level}"

class GenericRole:
    def __init__(self):
        self.role = ""
        self.role_description = ""
        self.generic_skills = []


class RoleLevel:
    def __init__(self):
        self.skills: List[SkillLevel] = []


class ContentParser:
    def __init__(self):
        with open("DDaTCFdrafttext.html") as html_file:
            self.soup = bs4.BeautifulSoup(html_file, "html.parser")
        self.generic_skills = {}
        self.generic_roles = {}
        self.role_levels = {}
        self.skill_levels = {}

    def process_content(self):
        for generic_role_title in self.soup.find_all("h1"):
            if generic_role_title.text != "" and generic_role_title.text[0:4] != "Land":
                self.generic_roles[generic_role_title.text] = self.process_role(generic_role_title)

    def process_role(self, next_role_tag: bs4.Tag):
        generic_role = GenericRole()
        generic_role.role = next_role_tag.text
        for current_sib in next_role_tag.next_siblings:
            if current_sib.name == "h1" or current_sib.text == "Read more":
                return generic_role
            elif current_sib.name == "h2" and current_sib.text[0:5] == "Intro":
                # generic role description
                generic_role.role_description = current_sib.next_sibling.text
            elif re.match("Skills required", current_sib.previous_sibling.text):
                # we're in the generic skills
                generic_role.generic_skills = self.process_generic_skills(current_sib)
            elif re.search(generic_role.role.lower(), current_sib.text.lower()) and current_sib.name == "h2":
                print(current_sib.next_sibling.next_sibling.contents)

    def process_generic_skills(self, skills_required_tag: bs4.Tag):
        generic_skills = [GenericSkill(list_item.text) for list_item in skills_required_tag.next_sibling.contents]
        return generic_skills


def main():
    parser = ContentParser()
    parser.process_content()
    # print(len(parser.generic_roles))
    # for key, value in parser.generic_roles.items():
    #     print(key, value.role_description, value.generic_skills)




if __name__ == '__main__':
    main()
