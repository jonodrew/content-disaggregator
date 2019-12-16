import csv
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
        self.role_levels = []


class RoleLevel:
    def __init__(self):
        self.name = ""
        self.skills: List[SkillLevel] = []

    def __repr__(self):
        return self.name


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
            elif current_sib.name == "h2":
                generic_role.role_levels.append(self.process_role_level(current_sib))

    def process_generic_skills(self, skills_required_tag: bs4.Tag):
        generic_skills = [GenericSkill(list_item.text) for list_item in skills_required_tag.next_sibling.contents]
        return generic_skills

    def process_role_level(self, role_level_tag: bs4.Tag):
        """
        This can't deal with specialisms in role levels. Content will need to be brought out separately
        :param role_level_tag:
        :type role_level_tag:
        :return:
        :rtype:
        """
        role_level = RoleLevel()
        role_level.name = role_level_tag.text
        for tag in role_level_tag.next_siblings:
            if tag.next_sibling.name == "ul" and (tag.previous_sibling.text[:6] == "Skills" or tag.text[:6] == "Skills"):
                role_level.skills = [SkillLevel(list_tag.text) for list_tag in tag.next_sibling.contents]
            elif tag.name == "h2":
                return role_level


def main():
    field_names = ["Role", "Role level", "Skill name", "Skill description", "Level", "Skill level"]
    parser = ContentParser()
    parser.process_content()
    with open("output_file.csv", 'w') as output_file:
        dict_writer = csv.DictWriter(output_file, field_names)
        dict_writer.writeheader()
        for key, value in parser.generic_roles.items():
            output = dict()
            output["Role"] = key
            for role in value.role_levels:
                output["Role level"] = role.name
                for skill in role.skills:
                    output["Skill name"] = skill.skill_name
                    output["Level"] = skill.level
                    output["Skill level"] = skill.skill_description
                    dict_writer.writerow(output)


if __name__ == '__main__':
    main()
