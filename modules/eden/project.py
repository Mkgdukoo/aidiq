# -*- coding: utf-8 -*-

""" Sahana Eden Project Model

    @author: Dominic König <dominic[at]aidiq.com>

    @copyright: 2011-2012 (c) Sahana Software Foundation
    @license: MIT

    Permission is hereby granted, free of charge, to any person
    obtaining a copy of this software and associated documentation
    files (the "Software"), to deal in the Software without
    restriction, including without limitation the rights to use,
    copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the
    Software is furnished to do so, subject to the following
    conditions:

    The above copyright notice and this permission notice shall be
    included in all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
    OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
    NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
    HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
    WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
    OTHER DEALINGS IN THE SOFTWARE.
"""

__all__ = ["S3ProjectModel",
           "project_rheader"]

import datetime

from gluon import *
from gluon.dal import Row, Rows
from gluon.storage import Storage
from gluon.sqlhtml import CheckboxesWidget
from ..s3 import *

# =============================================================================
class S3ProjectModel(S3Model):
    """ Project Model """

    names = ["project_theme",
             "project_hazard",
             "project_project",
             "project_organisation",
             "project_activity_type",
             "project_activity",
             "project_milestone",
             "project_site",
             "project_beneficiary_type",
             "project_beneficiary",
             "project_comment",
             "project_task",
             "project_time",
             "project_task_ireport",
             "project_task_job_role",
             "project_task_human_resource",
             "project_task_document",
             "project_task_project",
             "project_task_activity",
             "project_project_id",
             "project_activity_id",
             "project_task_id",
             "project_organisation_roles",
             "project_organisation_lead_role",
             "project_hfa_opts",
             "project_project_represent",
             ]

    def model(self):

        auth = current.auth
        db = current.db
        T = current.T
        request = current.request
        s3 = current.response.s3

        currency_type = s3.currency_type
        person_id = self.pr_person_id
        organisation_id = s3.org_organisation_id

        s3_date_format = self.settings.get_L10n_date_format()
        s3_datetime_represent = S3DateTime.datetime_represent
        s3_utc_represent = lambda dt: s3_datetime_represent(dt, utc=True)


        # Enable DRR extensions?
        drr = self.settings.get_project_drr()
        pca = self.settings.get_project_community_activity()

        NONE = current.messages.NONE
        UNKNOWN_OPT = current.messages.UNKNOWN_OPT

        # ---------------------------------------------------------------------
        # Theme
        #
        tablename = "project_theme"
        table = self.define_table(tablename,
                                  Field("name",
                                        length=128,
                                        notnull=True,
                                        unique=True),
                                  Field("comments"),
                                  format = "%(name)s",
                                  *s3.meta_fields())

        # Field configuration?

        # CRUD Strings?

        # Search Method?

        # Resource Configuration?

        # Reusable Field
        multi_theme_id = S3ReusableField("multi_theme_id",
                                         "list:reference project_theme",
                                         label = T("Themes"),
                                         sortby = "name",
                                         requires = IS_NULL_OR(IS_ONE_OF(db,
                                                                         "project_theme.id",
                                                                         "%(name)s",
                                                                         sort=True,
                                                                         multiple=True)),
                                         represent = lambda opt, row=None: \
                                                     self.multiref_represent(opt, "project_theme"),
                                         default = [],
                                         ondelete = "RESTRICT",
                                         widget = lambda f, v: \
                                                  CheckboxesWidgetS3.widget(f, v, cols = 3))

        # ---------------------------------------------------------------------
        # Hazard
        #
        tablename = "project_hazard"
        table = self.define_table(tablename,
                                  Field("name",
                                        length=128,
                                        notnull=True,
                                        unique=True),
                                  Field("comments"),
                                  format="%(name)s",
                                  *s3.meta_fields())

        # Field configuration?

        # CRUD Strings?

        # Search Method?

        # Resource Configuration?

        # Reusable Field
        multi_hazard_id = S3ReusableField("multi_hazard_id",
                                          "list:reference project_hazard",
                                          sortby = "name",
                                          label = T("Hazards"),
                                          requires = IS_NULL_OR(IS_ONE_OF(db,
                                                                          "project_hazard.id",
                                                                          "%(name)s",
                                                                          sort=True,
                                                                          multiple=True)),
                                          represent = lambda opt, row=None: \
                                                      self.multiref_represent(opt, "project_hazard"),
                                          ondelete = "RESTRICT",
                                          widget = lambda f, v: CheckboxesWidgetS3.widget(f, v, cols = 3))

        # ---------------------------------------------------------------------
        # Project
        #

        # HFA
        # @todo: localization?
        project_hfa_opts = {
            1: "HFA1: Ensure that disaster risk reduction is a national and a local priority with a strong institutional basis for implementation.",
            2: "HFA2: Identify, assess and monitor disaster risks and enhance early warning.",
            3: "HFA3: Use knowledge, innovation and education to build a culture of safety and resilience at all levels.",
            4: "HFA4: Reduce the underlying risk factors.",
            5: "HFA5: Strengthen disaster preparedness for effective response at all levels.",
        }

        sector_id = s3.org_sector_id

        countries_id = S3ReusableField("countries_id", "list:reference gis_location",
                                       label = T("Countries"),
                                       requires = IS_NULL_OR(IS_ONE_OF(db,
                                                                       "gis_location.id",
                                                                       "%(name)s",
                                                                       filterby = "level",
                                                                       filter_opts = ["L0"],
                                                                       sort=True,
                                                                       multiple=True)),
                                       represent = self.countries_represent,
                                       ondelete = "RESTRICT")

        tablename = "project_project"
        table = self.define_table(tablename,
                                  self.super_link("doc_id", "doc_entity"),
                                  organisation_id(
                                               #readable=False,
                                               #writable=False
                                              ),
                                  Field("name",
                                        label = T("Name"),
                                        # Require unique=True if using IS_NOT_ONE_OF like here (same table,
                                        # no filter) in order to allow both automatic indexing (faster)
                                        # and key-based de-duplication (i.e. before field validation)
                                        unique = True,
                                        requires = [IS_NOT_EMPTY(error_message=T("Please fill this!")),
                                                    IS_NOT_ONE_OF(db, "project_project.name")]),
                                  Field("code",
                                        label = T("Code"),
                                        readable=False,
                                        writable=False),
                                  Field("description", "text",
                                        label = T("Description")),
                                  Field("start_date", "date",
                                        label = T("Start date"),
                                        requires = IS_NULL_OR(IS_DATE(format = s3_date_format))),
                                  Field("end_date", "date",
                                        label = T("End date"),
                                        requires = IS_NULL_OR(IS_DATE(format = s3_date_format))),
                                  Field("duration",
                                        readable=False,
                                        writable=False,
                                        label = T("Duration")),

                                  currency_type(),
                                  Field("budget", "double",
                                        label = T("Budget")),
                                  sector_id(
                                            readable=False,
                                            writable=False,
                                            widget=lambda f, v: \
                                            CheckboxesWidget.widget(f, v, cols=3)),

                                  countries_id(
                                               readable=False,
                                               writable=False
                                              ),
                                  multi_hazard_id(readable=drr,
                                                  writable=drr),
                                  multi_theme_id(
                                                 readable=False,
                                                 writable=False
                                                ),
                                  Field("hfa", "list:integer",
                                        label = T("HFA Priorities"),
                                        readable=drr,
                                        writable=drr,
                                        requires = IS_NULL_OR(IS_IN_SET(project_hfa_opts,
                                                                        multiple = True)),
                                        represent = self.hfa_opts_represent,
                                        widget = CheckboxesWidgetS3.widget),

                                  Field("objectives", "text",
                                        readable = False,
                                        writable = False,
                                        label = T("Objectives")),
                                  format="%(name)s",
                                  *s3.meta_fields())

        # Field configuration?

        # CRUD Strings
        ADD_PROJECT = T("Add Project")
        s3.crud_strings[tablename] = Storage(
            title_create = ADD_PROJECT,
            title_display = T("Project Details"),
            title_list = T("List Projects"),
            title_update = T("Edit Project"),
            title_search = T("Search Projects"),
            title_upload = T("Import Project List"),
            subtitle_create = T("Add New Project"),
            subtitle_list = T("Projects"),
            subtitle_upload = T("Upload Project List"),
            label_list_button = T("List Projects"),
            label_create_button = ADD_PROJECT,
            label_delete_button = T("Delete Project"),
            msg_record_created = T("Project added"),
            msg_record_modified = T("Project updated"),
            msg_record_deleted = T("Project deleted"),
            msg_list_empty = T("No Projects currently registered"))

        # Search Method?

        # Resource Configuration
        self.configure(tablename,
                       super_entity="doc_entity",
                       deduplicate=self.project_project_deduplicate,
                       onvalidation=self.project_project_onvalidation,
                       onaccept=self.project_project_onaccept,
                       create_next=URL(c="project", f="project",
                                       args=["[id]", "activity"]),
                       list_fields=["id",
                                    "name",
                                    "organisation_id",
                                    #"countries_id",
                                    #"start_date",
                                    "end_date",
                                   ])
        # Reusable Field
        project_id = S3ReusableField("project_id", db.project_project,
                                     sortby="name",
                                     requires = IS_NULL_OR(IS_ONE_OF(db, "project_project.id",
                                                                     "%(name)s")),
                                     represent = self.project_represent,
                                     comment = DIV(A(ADD_PROJECT,
                                                     _class="colorbox",
                                                     _href=URL(c="project", f="project",
                                                               args="create",
                                                               vars=dict(format="popup")),
                                                     _target="top",
                                                     _title=ADD_PROJECT),
                                                   DIV(_class="tooltip",
                                                       _title="%s|%s" % (ADD_PROJECT,
                                                                         T("Add new project.")))),
                                     label = T("Project"),
                                     ondelete = "CASCADE")

        # Components
        # Organisations
        self.add_component("project_organisation", project_project="project_id")

        # Sites
        self.add_component("project_site", project_project="project_id")

        # Activities
        self.add_component("project_activity", project_project="project_id")

        # Milestones
        self.add_component("project_milestone", project_project="project_id")

        # Beneficiaries
        self.add_component("project_beneficiary", project_project="project_id")

        # Tasks
        self.add_component("project_task",
                           project_project=Storage(
                                link="project_task_project",
                                joinby="project_id",
                                key="task_id",
                                actuate="replace",
                                autocomplete="name",
                                autodelete=False))

        # ---------------------------------------------------------------------
        # Project Organisation
        #
        project_organisation_roles = {
            1: T("Lead Implementer"), # T("Host National Society")
            2: T("Partner"), # T("Partner National Society")
            3: T("Donor"),
            4: T("Customer"), # T("Beneficiary")?
        }
        project_organisation_lead_role = 1

        tablename = "project_organisation"
        table = self.define_table(tablename,
                                  project_id(),
                                  organisation_id(),
                                  Field("role", "integer",
                                        requires = IS_NULL_OR(IS_IN_SET(project_organisation_roles)),
                                        represent = lambda opt, row=None: \
                                                    project_organisation_roles.get(opt, NONE)),
                                  Field("amount", "double",
                                        requires = IS_FLOAT_AMOUNT(),
                                        represent = lambda v, row=None: \
                                                    IS_FLOAT_AMOUNT.represent(v, precision=2),
                                        widget = IS_FLOAT_AMOUNT.widget,
                                        label = T("Funds Contributed by this Organization")),
                                  currency_type(),
                                  *s3.meta_fields())

        # Field configuration?

        # CRUD Strings
        ADD_PROJECT_ORG = T("Add Organization to Project")
        LIST_PROJECT_ORG = T("List Project Organizations")
        s3.crud_strings[tablename] = Storage(
            title_create = ADD_PROJECT_ORG,
            title_display = T("Project Organization Details"),
            title_list = LIST_PROJECT_ORG,
            title_update = T("Edit Project Organization"),
            title_search = T("Search Project Organizations"),
            title_upload = T("Import Project Organizations"),
            subtitle_create = T("Add Organization to Project"),
            subtitle_list = T("Project Organizations"),
            label_list_button = LIST_PROJECT_ORG,
            label_create_button = ADD_PROJECT_ORG,
            label_delete_button = T("Remove Organization from Project"),
            msg_record_created = T("Organization added to Project"),
            msg_record_modified = T("Project Organization updated"),
            msg_record_deleted = T("Organization removed from Project"),
            msg_list_empty = T("No Organizations for this Project"))

        # Search Method?

        # Resource Configuration
        self.configure(tablename,
                       deduplicate=self.project_organisation_deduplicate,
                       onvalidation=self.project_organisation_onvalidation)

        # Reusable Field

        # Components

        # ---------------------------------------------------------------------
        # Activity Type
        #
        tablename = "project_activity_type"
        table = self.define_table(tablename,
                                Field("name", length=128,
                                      notnull=True, unique=True),
                                format="%(name)s",
                                *s3.meta_fields())

        # Field configuration?

        # CRUD Strings
        ADD_ACTIVITY_TYPE = T("Add Activity Type")
        LIST_ACTIVITY_TYPES = T("List of Activity Types")
        s3.crud_strings[tablename] = Storage(
            title_create = ADD_ACTIVITY_TYPE,
            title_display = T("Activity Type"),
            title_list = LIST_ACTIVITY_TYPES,
            title_update = T("Edit Activity Type"),
            title_search = T("Search for Activity Type"),
            subtitle_create = T("Add New Activity Type"),
            subtitle_list = T("All Activity Types"),
            label_list_button = LIST_ACTIVITY_TYPES,
            label_create_button = ADD_ACTIVITY_TYPE,
            msg_record_created = T("Activity Type Added"),
            msg_record_modified = T("Activity Type Updated"),
            msg_record_deleted = T("Activity Type Deleted"),
            msg_list_empty = T("No Activity Types Found")
        )

        # Search Method?

        # Resource Configuration?

        # Reusable Fields
        activity_type_id = S3ReusableField("activity_type_id",
                                           db.project_activity_type,
                                           sortby="name",
                                           requires = IS_NULL_OR(IS_ONE_OF(db,
                                                                           "project_activity_type.id",
                                                                           "%(name)s",
                                                                           sort=True)),
                                           represent = lambda id, row=None: \
                                                       s3_get_db_field_value(tablename = "project_activity_type",
                                                                             fieldname = "name",
                                                                             look_up_value = id),
                                           label = T("Activity Type"),
                                           comment = self.activity_type_comment(ADD_ACTIVITY_TYPE),
                                           ondelete = "RESTRICT")

        multi_activity_type_id = S3ReusableField("multi_activity_type_id",
                                                 "list:reference project_activity_type",
                                                 sortby = "name",
                                                 label = T("Types of Activities"),
                                                 requires = IS_NULL_OR(IS_ONE_OF(db,
                                                                                 "project_activity_type.id",
                                                                                 "%(name)s",
                                                                                 sort=True,
                                                                                 multiple=True)),
                                                 represent = lambda opt, row=None: \
                                                             self.multiref_represent(opt,
                                                                                     "project_activity_type"),
                                                 #comment = skill_help,
                                                 default = [],
                                                 widget = lambda f, v: \
                                                    CheckboxesWidgetS3.widget(f, v, col=3),
                                                 ondelete = "RESTRICT")

        # ---------------------------------------------------------------------
        # Project Activity
        #
        tablename = "project_activity"
        table = self.define_table(tablename,
                                  self.super_link("doc_id", "doc_entity"),
                                  project_id(),
                                  Field("name",
                                        label = T("Short Description"),
                                        requires=IS_NOT_EMPTY()),
                                  s3.location_id(
                                        readable = False,
                                        writable = False,
                                        widget = S3LocationSelectorWidget(hide_address=True)),
                                  multi_activity_type_id(),
                                  Field("time_estimated", "double",
                                        label = "%s (%s)" % (T("Time Estimate"),
                                                             T("hours"))),
                                  Field("time_actual", "double",
                                        # Gets populated from constituent Tasks
                                        writable=False,
                                        label = "%s (%s)" % (T("Time Taken"),
                                                             T("hours"))),
                                  s3.comments(),
                                  format="%(name)s",
                                  *s3.meta_fields())

        # Field configuration
        if pca:
            table.name.readable = False
            table.name.writable = False
            table.name.requires = None

        # CRUD Strings
        if pca:
            ADD_ACTIVITY = T("Add Community")
            LIST_ACTIVITIES = T("List Communities")
            s3.crud_strings[tablename] = Storage(
                title_create = ADD_ACTIVITY,
                title_display = T("Community Details"),
                title_list = LIST_ACTIVITIES,
                title_update = T("Edit Community Details"),
                title_search = T("Search Community"),
                title_upload = T("Import Community Data"),
                title_report = T("Who is doing What Where"),
                subtitle_create = T("Add New Community"),
                subtitle_list = T("Communities"),
                subtitle_report = T("Communities"),
                label_list_button = LIST_ACTIVITIES,
                label_create_button = ADD_ACTIVITY,
                msg_record_created = T("Community Added"),
                msg_record_modified = T("Community Updated"),
                msg_record_deleted = T("Community Deleted"),
                msg_list_empty = T("No Communities Found")
            )
        else:
            ADD_ACTIVITY = T("Add Activity")
            LIST_ACTIVITIES = T("List Activities")
            s3.crud_strings[tablename] = Storage(
                title_create = ADD_ACTIVITY,
                title_display = T("Activity Details"),
                title_list = LIST_ACTIVITIES,
                title_update = T("Edit Activity"),
                title_search = T("Search Activities"),
                title_upload = T("Import Activity Data"),
                title_report = T("Budget Line Utilisation"),
                subtitle_create = T("Add New Activity"),
                subtitle_list = T("Activities"),
                subtitle_report = T("Activities"),
                label_list_button = LIST_ACTIVITIES,
                label_create_button = ADD_ACTIVITY,
                msg_record_created = T("Activity Added"),
                msg_record_modified = T("Activity Updated"),
                msg_record_deleted = T("Activity Deleted"),
                msg_list_empty = T("No Activities Found")
            )

        # Virtual Fields
        table.virtualfields.append(S3ProjectActivityVirtualfields())

        # Search Method
        if pca:
            project_activity_search = S3Search(field="location_id$name")
        else:
            project_activity_search = S3Search(field="name")

        # Resource Configuration
        analyze_fields = [#(T("Organization"), "organisation"),
                          (T("Project"), "project_id"),
                          (T("Activity Type"), "multi_activity_type_id"),
                          (T("Time Estimated"), "time_estimated"),
                          (T("Time Actual"), "time_actual"),
                          #(T("Theme"), "project_id$multi_theme_id"),
                          #(T("Hazard"), "project_id$multi_hazard_id"),
                          #(T("HFA"), "project_id$hfa")
                          ]
        #lh = self.settings.get_gis_default_location_hierarchy()
        #lh = [(lh[opt], opt) for opt in lh]
        #analyze_fields.extend(lh)
        #analyze_fields.append("location_id")
        if not pca:
            analyze_fields.insert(2, (T("Activity"), "name"))

        self.configure(tablename,
                       super_entity="doc_entity",
                       create_next=URL(c="project", f="activity",
                                       args=["[id]", "task"]),
                       search_method=project_activity_search,
                       onaccept=self.project_activity_onaccept,
                       deduplicate=self.project_activity_deduplicate,
                       analyze_rows=analyze_fields,
                       analyze_cols=analyze_fields,
                       analyze_fact=analyze_fields)

        # Reusable Field
        activity_id = S3ReusableField("activity_id", db.project_activity,
                                      sortby="name",
                                      requires = IS_NULL_OR(IS_ONE_OF(db,
                                                                      "project_activity.id",
                                                                      "%(name)s",
                                                                      sort=True)),
                                      represent = lambda id, row=None: \
                                                  s3_get_db_field_value(tablename = "project_activity",
                                                                        fieldname = "name",
                                                                        look_up_value = id),
                                      label = T("Activity"),
                                      comment = DIV(A(ADD_ACTIVITY,
                                                      _class="colorbox",
                                                      _href=URL(c="project", f="activity",
                                                                args="create",
                                                                vars=dict(format="popup")),
                                                      _target="top",
                                                      _title=ADD_ACTIVITY)),
                                      ondelete = "CASCADE")

        # Components

        #Beneficiaries
        self.add_component("project_beneficiary",
                           project_activity="activity_id")

        # Tasks
        self.add_component("project_task",
                           project_activity=Storage(
                                link="project_task_activity",
                                joinby="activity_id",
                                key="task_id",
                                actuate="embed",
                                autocomplete="name",
                                autodelete=False))


        # ---------------------------------------------------------------------
        # Project Site
        #
        tablename = "project_site"
        table = self.define_table(tablename,
                                  self.super_link("site_id", "org_site"),
                                  project_id(),
                                  Field("name", notnull=True,
                                        length=64, # Mayon Compatibility
                                        label = T("Name")),
                                  s3.location_id(),
                                  multi_activity_type_id(),
                                  *(s3.address_fields() + s3.meta_fields()))


        # Field configuration
        # CRUD Strings
        # Search Method
        # Resource Configuration
        # Reusable Field

        # CRUD strings
        ADD_PROJECT_SITE = T("Add Project Site")
        LIST_PROJECT_SITE = T("List Project Sites")
        s3.crud_strings[tablename] = Storage(
            title_create = ADD_PROJECT_SITE,
            title_display = T("Project Site Details"),
            title_list = LIST_PROJECT_SITE,
            title_update = T("Edit Project Site"),
            title_search = T("Search Project Sites"),
            title_upload = T("Import Project Sites"),
            subtitle_create = T("Add New Project Site"),
            subtitle_list = T("Sites"),
            label_list_button = LIST_PROJECT_SITE,
            label_create_button = ADD_PROJECT_SITE,
            label_delete_button = T("Delete Project Site"),
            msg_record_created = T("Project Site added"),
            msg_record_modified = T("Project Site updated"),
            msg_record_deleted = T("Project Site deleted"),
            msg_list_empty = T("No Project Sites currently registered"))

        # Reusable field for other tables to reference
        project_site_comment = DIV(A(ADD_PROJECT_SITE,
                                     _class="colorbox",
                                     _href=URL(c="project", f="site",
                                               args="create",
                                               vars=dict(format="popup")),
                                     _target="top",
                                     _title=ADD_PROJECT_SITE),
                                   DIV( _class="tooltip",
                                        _title="%s|%s" % (
                                            ADD_PROJECT_SITE,
                                            T("If you don't see the site in the list, you can add a new one by clicking link 'Add Project Site'.")
                                            )
                                       )
                                   )

        project_site_id = S3ReusableField("project_site_id", db.project_site,
                                          #sortby="default/indexname",
                                          requires = IS_NULL_OR(IS_ONE_OF(db, "project_site.id", "%(name)s")),
                                          represent = lambda id, row=None: \
                                                      (id and [db(db.project_site.id == id).select(db.project_site.name,
                                                                                                   limitby=(0, 1)).first().name] or [NONE])[0],
                                          label = T("Project Site"),
                                          comment = s3.org_office_comment,
                                          ondelete = "CASCADE")

        self.configure(tablename,
                        super_entity="org_site",
                        onvalidation=s3.address_onvalidation)

        # ---------------------------------------------------------------------
        # Project Beneficiary Type
        #
        tablename = "project_beneficiary_type"
        table = self.define_table(tablename,
                                  Field("name",
                                        length=128,
                                        unique=True,
                                        requires = IS_EMPTY_OR(IS_NOT_IN_DB(db,
                                                                            "project_beneficiary_type.name"))),
                                  *s3.meta_fields())

        # Field configuration?

        # CRUD Strings
        ADD_BNF_TYPE = T("Add Beneficiary Type")
        LIST_BNF_TYPE = T("List Beneficiary Types")
        s3.crud_strings[tablename] = Storage(
            title_create = ADD_BNF_TYPE,
            title_display = T("Beneficiary Type"),
            title_list = LIST_BNF_TYPE,
            title_update = T("Edit Beneficiary Type"),
            title_search = T("Search Beneficiary Types"),
            subtitle_create = T("Add New Beneficiary Type"),
            subtitle_list = T("Beneficiary Types"),
            label_list_button = LIST_BNF_TYPE,
            label_create_button = ADD_BNF_TYPE,
            msg_record_created = T("Beneficiary Type Added"),
            msg_record_modified = T("Beneficiary Type Updated"),
            msg_record_deleted = T("Beneficiary Type Deleted"),
            msg_list_empty = T("No Beneficiary Types Found")
        )

        # Search Method?

        # Resource Configuration?

        # Reusable Field
        bnf_type = S3ReusableField("bnf_type", db.project_beneficiary_type,
                                   requires = IS_NULL_OR(IS_ONE_OF(db,
                                                                   "project_beneficiary_type.id",
                                                                   self.beneficiary_type_represent)),
                                   represent = self.beneficiary_type_represent,
                                   label = T("Beneficiary Type"),
                                   comment = DIV(A(ADD_BNF_TYPE,
                                                   _class="colorbox",
                                                   _href=URL(c="project", f="beneficiary_type",
                                                             args="create",
                                                             vars=dict(format="popup",
                                                                       child="bnf_type")),
                                                   _target="top",
                                                   _title=ADD_BNF_TYPE),
                                                 DIV(_class="tooltip",
                                                     _title="%s|%s" % (ADD_BNF_TYPE,
                                                                       T("Add a new beneficiary type")))),
                                   ondelete = "CASCADE")

        # ---------------------------------------------------------------------
        # Project Beneficiary
        #
        tablename = "project_beneficiary"
        table = self.define_table(tablename,
                                  # populated automatically
                                  project_id(readable=False,
                                             writable=False),
                                  activity_id(comment=None),
                                  bnf_type(),
                                  Field("number", "integer",
                                        requires = IS_NULL_OR(IS_INT_IN_RANGE(0, 99999999))),
                                  s3.comments(),
                                  *s3.meta_fields())

        # Field configuration?

        # CRUD Strings
        ADD_BNF = T("Add Beneficiaries")
        LIST_BNF = T("List Beneficiaries")
        s3.crud_strings[tablename] = Storage(
            title_create = ADD_BNF,
            title_display = T("Beneficiaries Details"),
            title_list = LIST_BNF,
            title_update = T("Edit Beneficiaries"),
            title_search = T("Search Beneficiaries"),
            title_report = T("Beneficiary Report"),
            subtitle_create = T("Add New Beneficiaries"),
            subtitle_list = T("Beneficiaries"),
            label_list_button = LIST_BNF,
            label_create_button = ADD_BNF,
            msg_record_created = T("Beneficiaries Added"),
            msg_record_modified = T("Beneficiaries Updated"),
            msg_record_deleted = T("Beneficiaries Deleted"),
            msg_list_empty = T("No Beneficiaries Found")
        )

        # Search Method?

        # Resource Configuration
        self.configure(tablename,
                        onaccept=self.project_beneficiary_onaccept,
                        deduplicate=self.project_beneficiary_deduplicate,
                        #analyze_filter=[
                            #s3base.S3SearchOptionsWidget(field=["project_id"],
                                                         #name="project",
                                                         #label=T("Project"))
                        #],
                        analyze_rows=[
                                      "activity_id",
                                      "project_id",
                                      "project_id$multi_hazard_id",
                                      "project_id$multi_theme_id",
                                      "activity_id$multi_activity_type_id"
                                     ],
                        analyze_cols=[
                                      "bnf_type",
                                     ],
                        analyze_fact=["number"],
                        analyze_method=["sum"])

        # Reusable Field
        beneficiary_id = S3ReusableField("beneficiary_id", db.project_beneficiary,
                                         sortby="name",
                                         requires = IS_NULL_OR(IS_ONE_OF(db,
                                                                         "project_beneficiary.id",
                                                                         "%(type)s",
                                                                         sort=True)),
                                         represent = lambda id, row=None: \
                                                     s3_get_db_field_value(tablename = "project_beneficiary",
                                                                           fieldname = "type",
                                                                           look_up_value = id),
                                         label = T("Beneficiaries"),
                                         comment = DIV(A(ADD_BNF,
                                                         _class="colorbox",
                                                         _href=URL(c="project",
                                                                   f="beneficiary",
                                                                   args="create",
                                                                   vars=dict(format="popup")),
                                                         _target="top",
                                                         _title=ADD_BNF)),
                                         ondelete = "SET NULL")

        # ---------------------------------------------------------------------
        # Project Milestone
        #
        tablename = "project_milestone"
        table = self.define_table(tablename,
                                  # Stage Report
                                  self.super_link("doc_id", "doc_entity"),
                                  project_id(),
                                  Field("name",
                                        label = T("Short Description"),
                                        requires=IS_NOT_EMPTY()),
                                  Field("date", "date",
                                        label = T("Date"),
                                        requires = IS_NULL_OR(IS_DATE(format = s3_date_format))),
                                  s3.comments(),
                                  format="%(name)s",
                                  *s3.meta_fields())

        # CRUD Strings
        ADD_MILESTONE = T("Add Milestone")
        s3.crud_strings[tablename] = Storage(
            title_create = ADD_MILESTONE,
            title_display = T("Milestone Details"),
            title_list = T("List Milestones"),
            title_update = T("Edit Milestone"),
            title_search = T("Search Milestones"),
            title_upload = T("Import Milestone Data"),
            subtitle_create = T("Add New Milestone"),
            subtitle_list = T("Milestones"),
            subtitle_report = T("Milestones"),
            label_list_button = T("List Milestones"),
            label_create_button = ADD_MILESTONE,
            msg_record_created = T("Milestone Added"),
            msg_record_modified = T("Milestone Updated"),
            msg_record_deleted = T("Milestone Deleted"),
            msg_list_empty = T("No Milestones Found")
        )

        # Reusable Field
        milestone_id = S3ReusableField("milestone_id", db.project_milestone,
                                       sortby="name",
                                       requires = IS_NULL_OR(IS_ONE_OF(db, "project_milestone.id",
                                                                       "%(name)s")),
                                       represent = self.milestone_represent,
                                       comment = DIV(A(ADD_MILESTONE,
                                                       _class="colorbox",
                                                       _href=URL(c="project", f="milestone",
                                                                 args="create",
                                                                 vars=dict(format="popup")),
                                                       _target="top",
                                                       _title=ADD_MILESTONE),
                                                     DIV(_class="tooltip",
                                                         _title="%s|%s" % (ADD_MILESTONE,
                                                                           T("A project milestone marks a significant date in the calendar which shows that progress towards the overall objective is being made.")))),
                                       label = T("Milestone"),
                                       ondelete = "RESTRICT")

        # ---------------------------------------------------------------------
        # Tasks
        #
        # Tasks can be linked to Activities or directly to Projects
        # - they can also be used by the Event/Scenario modules
        #
        # @ToDo: Recurring tasks
        #
        project_task_status_opts = {
            #1: T("Draft"),
            2: T("New"),
            3: T("Assigned"),
            4: T("On Hold"),
            5: T("Feedback"),
            6: T("Cancelled"),
            7: T("Blocked"),
            8: T("Completed"),
            #9: T("Verified"),
            #99: T("unspecified")
        }

        project_task_active_statuses = [2, 3, 5, 7]
        
        project_task_priority_opts = {
            1:T("Urgent"),
            2:T("High"),
            3:T("Normal"),
            4:T("Low")
        }

        staff = auth.s3_has_role("STAFF")

        tablename = "project_task"
        table = self.define_table(tablename,
                                  self.super_link("doc_id", "doc_entity"),
                                  Field("template", "boolean",
                                        default=False,
                                        readable=False,
                                        writable=False),
                                  Field("status", "integer",
                                        requires = IS_IN_SET(project_task_status_opts,
                                                             zero=None),
                                        default = 2,
                                        readable = staff,
                                        writable = staff,
                                        label = T("Status"),
                                        represent = lambda opt, row=None: \
                                                    project_task_status_opts.get(opt,
                                                                                 UNKNOWN_OPT)),
                                  Field("name",
                                        label = T("Short Description"),
                                        length=100,
                                        notnull=True,
                                        requires = IS_NOT_EMPTY()),
                                  Field("source",
                                        label = T("Source")),
                                  Field("description", "text",
                                        label = T("Detailed Description/URL"),
                                        comment = DIV(_class="tooltip",
                                                      _title="%s|%s" % (T("Detailed Description/URL"),
                                                                        T("Please provide as much detail as you can, including the URL(s) where the bug occurs or you'd like the new feature to go.")))),
                                  Field("priority", "integer",
                                        requires = IS_IN_SET(project_task_priority_opts,
                                                             zero=None),
                                        default = 3,
                                        label = T("Priority"),
                                        represent = lambda opt, row=None: \
                                                    project_task_priority_opts.get(opt,
                                                                                   UNKNOWN_OPT)),
                                  # Could be an Organisation, a Team or a Person
                                  self.super_link("pe_id", "pr_pentity",
                                                  readable = staff,
                                                  writable = staff,
                                                  label = T("Assigned to"),
                                                  represent = lambda id, row=None: \
                                                              s3.pr_pentity_represent(id, show_label=False),
                                                  # @ToDo: Widget
                                                  #widget = S3PentityWidget(),
                                                  #comment = DIV(_class="tooltip",
                                                  #              _title="%s|%s" % (T("Assigned to"),
                                                  #                                T("Enter some characters to bring up a list of possible matches")))
                                                  ),
                                  Field("date_due", "datetime",
                                        label = T("Date Due"),
                                        readable = staff,
                                        writable = staff,
                                        requires = [IS_EMPTY_OR(
                                                    IS_UTC_DATETIME_IN_RANGE(
                                                        minimum=request.utcnow - datetime.timedelta(days=1),
                                                        error_message="%s %%(min)s!" %
                                                                      T("Enter a valid future date")))],
                                        widget = S3DateTimeWidget(past=0,
                                                                  future=8760),  # Hours, so 1 year
                                        represent = lambda v, row=None: S3DateTime.datetime_represent(v, utc=True)),
                                  milestone_id(
                                        readable = staff,
                                        writable = staff,
                                        ),
                                  Field("time_estimated", "double",
                                        readable = staff,
                                        writable = staff,
                                        label = "%s (%s)" % (T("Time Estimate"),
                                                             T("hours"))),
                                  Field("time_actual", "double",
                                        readable = staff,
                                        # This comes from the Time component
                                        writable=False,
                                        label = "%s (%s)" % (T("Time Taken"),
                                                             T("hours"))),
                                  s3.org_site_id,
                                  s3.location_id(label=T("Deployment Location"),
                                              readable=False,
                                              writable=False
                                              ),
                                  *s3.meta_fields())

        # Field configurations
        # Comment these if you don't need a Site associated with Tasks
        #table.site_id.readable = table.site_id.writable = True
        #table.site_id.label = T("Check-in at Facility") # T("Managing Office")

        # CRUD Strings
        ADD_TASK = T("Add Task")
        LIST_TASKS = T("List Tasks")
        s3.crud_strings[tablename] = Storage(
            title_create = ADD_TASK,
            title_display = T("Task Details"),
            title_list = LIST_TASKS,
            title_update = T("Edit Task"),
            title_search = T("Search Tasks"),
            title_upload = T("Import Tasks"),
            subtitle_create = T("Add New Task"),
            subtitle_list = T("Tasks"),
            label_list_button = LIST_TASKS,
            label_create_button = ADD_TASK,
            msg_record_created = T("Task added"),
            msg_record_modified = T("Task updated"),
            msg_record_deleted = T("Task deleted"),
            msg_list_empty = T("No tasks currently registered"))

        # Search Method?

        # Resource Configuration
        self.configure(tablename,
                       super_entity="doc_entity",
                       copyable=True,
                       orderby="project_task.priority",
                       onvalidation=self.task_onvalidation,
                       create_onaccept=self.task_create_onaccept,
                       list_fields=["id",
                                    #"urgent",
                                    "priority",
                                    "status",
                                    "name",
                                    "pe_id",
                                    "created_on",
                                    "date_due",
                                    #"site_id"
                                    ],
                       extra="description")

        # Reusable field
        task_id = S3ReusableField("task_id", db.project_task,
                                  label = T("Task"),
                                  sortby="name",
                                  requires = IS_NULL_OR(IS_ONE_OF(db, "project_task.id", "%(name)s")),
                                  represent = lambda id, row=None: \
                                                (id and [db.project_task[id].name] or [NONE])[0],
                                  comment = DIV(A(ADD_TASK,
                                                  _class="colorbox",
                                                  _href=URL(c="project", f="task",
                                                            args="create",
                                                            vars=dict(format="popup")),
                                                  _target="top",
                                                  _title=ADD_TASK),
                                                DIV(_class="tooltip",
                                                    _title="%s|%s" % (ADD_TASK,
                                                                      T("A task is a piece of work that an individual or team can do in 1-2 days")))),
                                  ondelete = "CASCADE")

        # Components
        # Projects (for imports)
        self.add_component("project_project",
                           project_task=Storage(
                                link="project_task_project",
                                joinby="task_id",
                                key="project_id",
                                actuate="embed",
                                autocomplete="name",
                                autodelete=False))

        # Job roles
        self.add_component("hrm_job_role",
                           project_task=Storage(
                                link="project_task_job_role",
                                joinby="task_id",
                                key="job_role_id",
                                actuate="embed",
                                autocomplete="name",
                                autodelete=False))

        # Human Resources (assigned)
        self.add_component("hrm_human_resource",
                           project_task=Storage(
                                link="project_task_human_resource",
                                joinby="task_id",
                                key="human_resource_id",
                                actuate="embed",
                                autocomplete="name",
                                autodelete=False))

        # Requests
        self.add_component("req_req",
                           project_task=Storage(
                                link="project_task_req",
                                joinby="task_id",
                                key="req_id",
                                actuate="embed",
                                autocomplete="request_number",
                                autodelete=False))

        # Time
        self.add_component("project_time", project_task="task_id")

        # ---------------------------------------------------------------------
        # Link Tasks <-> Projects
        #
        tablename = "project_task_project"
        table = self.define_table(tablename,
                                  task_id(),
                                  project_id(),
                                  *s3.meta_fields())

        # Field configuration
        # CRUD Strings
        # Search Method
        # Resource Configuration
        # Reusable Field

        # ---------------------------------------------------------------------
        # Link task <-> activity
        #
        # Tasks <> Activities
        tablename = "project_task_activity"
        table = self.define_table(tablename,
                                  task_id(),
                                  activity_id(),
                                  *s3.meta_fields())

        # Field configuration
        # CRUD Strings
        # Search Method
        # Resource Configuration
        # Reusable Field

        # ---------------------------------------------------------------------
        # Link Task <-> Human Resources, Task <-> Job roles
        #
        htable = self.table("hrm_human_resource", None)
        if htable is not None:

            human_resource_id = s3.human_resource_id
            job_role_id = s3.hrm_job_role_id

            # Tasks <> Human Resources
            tablename = "project_task_human_resource"
            table = self.define_table(tablename,
                                      task_id(),
                                      human_resource_id(),
                                      *s3.meta_fields())

            # Tasks <> Job Roles
            tablename = "project_task_job_role"
            table = self.define_table(tablename,
                                      task_id(),
                                      job_role_id(),
                                      *s3.meta_fields())

        # ---------------------------------------------------------------------
        # Link tasks <-> incident reports
        #
        itable = self.table("irg_ireport", None)
        if itable is not None:

            ireport_id = s3.ireport_id

            tablename = "project_task_ireport"
            table = self.define_table(tablename,
                                      task_id(),
                                      ireport_id(),
                                      *s3.meta_fields())

        # ---------------------------------------------------------------------
        # Project comment
        #
        # @ToDo: Attachments?
        #
        # Parent field allows us to:
        #  * easily filter for top-level threads
        #  * easily filter for next level of threading
        #  * hook a new reply into the correct location in the hierarchy
        #
        tablename = "project_comment"
        table = self.define_table(tablename,
                                  Field("parent", "reference project_comment",
                                        requires = IS_EMPTY_OR(IS_ONE_OF(db,
                                                                         "project_comment.id")),
                                        readable=False),
                                  #project_id(),
                                  #activity_id(),
                                  task_id(),
                                  Field("body", "text",
                                        notnull=True,
                                        label = T("Comment")),
                                  *s3.meta_fields())

        # Field configuration?

        # CRUD Strings?

        # Search Method?

        # Resource Configuration
        self.configure(tablename,
                       list_fields=["id",
                                    "task_id",
                                    "created_by",
                                    "modified_on"
                                    ])

        # Reusable Field?

        # ---------------------------------------------------------------------
        # Project Time
        # - used to Log hours spent on a Task
        #
        tablename = "project_time"
        table = self.define_table(tablename,
                                  task_id(),
                                  person_id(default=auth.s3_logged_in_person()),
                                  Field("date", "datetime",
                                        label = T("Date"),
                                        requires = IS_EMPTY_OR(IS_UTC_DATETIME()),
                                        represent = s3_utc_represent,
                                        widget = S3DateTimeWidget(past=8760, # Hours, so 1 year
                                                                  future=0),
                                        default = request.utcnow),
                                  Field("hours", "double",
                                        label = "%s (%s)" % (T("Time"),
                                                             T("hours"))),
                                  s3.comments(),
                                  format="%(comments)s",
                                  *s3.meta_fields())

        # CRUD Strings
        ADD_TIME = T("Log Time Spent")
        s3.crud_strings[tablename] = Storage(
            title_create = ADD_TIME,
            title_display = T("Logged Time Details"),
            title_list = T("List Logged Time"),
            title_update = T("Edit Logged Time"),
            title_search = T("Search Logged Time"),
            title_upload = T("Import Logged Time data"),
            title_report = T("Last Week's Work"),
            subtitle_create = T("Log New Time"),
            subtitle_list = T("Logged Time"),
            subtitle_report = T("Logged Time"),
            label_list_button = T("List Logged Time"),
            label_create_button = ADD_TIME,
            msg_record_created = T("Time Logged"),
            msg_record_modified = T("Time Log Updated"),
            msg_record_deleted = T("Time Log Deleted"),
            msg_list_empty = T("No Time Logged")
        )
        if "rows" in request.get_vars and request.get_vars.rows == "project":
            s3.crud_strings[tablename].title_report = T("Project Income Allocation")

        # Virtual Fields
        table.virtualfields.append(S3ProjectTimeVirtualfields())

        self.configure(tablename,
                       onaccept=self.time_onaccept,
                       list_fields=["id",
                                    (T("Project"), "project"),
                                    "task_id",
                                    "person_id",
                                    "date",
                                    "hours",
                                    "comments",
                                    ])

        # ---------------------------------------------------------------------
        # Pass variables back to global scope (response.s3.*)
        #
        return dict(
            project_project_id = project_id,
            project_activity_id = activity_id,
            project_task_id = task_id,
            project_task_active_statuses = project_task_active_statuses,
            project_organisation_roles = project_organisation_roles,
            project_organisation_lead_role = project_organisation_lead_role,
            project_hfa_opts = project_hfa_opts,
            project_project_represent = self.project_represent,
        )

    # -------------------------------------------------------------------------
    def defaults(self):
        """ Safe defaults for model-global names if module is disabled """

        dummy = S3ReusableField("dummy_id", "integer",
                                readable=False,
                                writable=False)

        return Storage(
            project_project_id = lambda: dummy("project_id"),
            project_activity_id = lambda: dummy("activity_id"),
            project_task_id = lambda: dummy("task_id"),
            project_project_represent = lambda v, r: current.messages.NONE
        )

    # -------------------------------------------------------------------------
    @staticmethod
    def multiref_represent(opts, tablename, represent_string = "%(name)s"):
        """
            Represent a list of references

            @param opt: the current value or list of values
            @param tablename: the referenced table
            @param represent_string: format string to represent the records
        """

        DEFAULT = ""

        db = current.db
        UNKNOWN_OPT = current.messages.UNKNOWN_OPT

        table = S3Model.table(tablename, None)
        if table is None:
            return DEFAULT

        if not isinstance(opts, (list, tuple)):
            opts = [opts]

        rows = db(table.id.belongs(opts)).select()
        rstr = Storage([(str(row.id), row) for row in rows])
        keys = rstr.keys()
        represent = lambda o: str(o) in keys and \
                              represent_string % rstr[str(o)] or UNKNOWN_OPT
        vals = [represent(o) for o in opts]

        if len(opts) > 1:
            vals = ", ".join(vals)
        else:
            vals = len(vals) and vals[0] or DEFAULT

        return vals

    # ---------------------------------------------------------------------
    @staticmethod
    def countries_represent(locations, row=None):
        """ FK representation """

        db = current.db

        if isinstance(locations, Rows):
            try:
                locations = [r.name for r in locations]
                return ", ".join(locations)
            except:
                locations = [r.id for r in locations]
        if not isinstance(locations, list):
            locations = [locations]
        table = db.gis_location
        query = table.id.belongs(locations)
        rows = db(query).select(table.name)
        return S3ProjectModel.countries_represent(rows)

    # ---------------------------------------------------------------------
    @staticmethod
    def project_represent(id, row=None, show_link=True):
        """ FK representation """

        db = current.db
        NONE = current.messages.NONE

        if id:
            val = (id and [db.project_project[id].name] or [NONE])[0]
            if not show_link:
                return val
            return A(val, _href = URL(c="project",
                                      f="project",
                                      args=[id]))
        else:
            return NONE

    # ---------------------------------------------------------------------
    @staticmethod
    def milestone_represent(id, row=None):
        """ FK representation """

        db = current.db
        NONE = current.messages.NONE

        if id:
            val = (id and [db.project_milestone[id].name] or [NONE])[0]
            return val
        else:
            return NONE

    # ---------------------------------------------------------------------
    @staticmethod
    def project_project_onvalidation(form):
        """ Form validation """

        if not form.vars.code and "name" in form.vars:
            # Populate code from name
            form.vars.code = form.vars.name
        return

    # ---------------------------------------------------------------------
    @staticmethod
    def project_project_onaccept(form):
        """ Set the project to be owned by the customer """

        db = current.db
        s3db = current.s3db

        if "organisation_id" in form.vars:
            # Set Project to be owned by this Customer
            organisation_id = form.vars.organisation_id
            otable = s3db.org_organisation
            query = (otable.id == organisation_id)
            role = db(query).select(otable.owned_by_organisation,
                                    limitby=(0, 1)).first()
            if role:
                table = s3db.project_project
                query = (table.id == form.vars.id)
                db(query).update(owned_by_organisation=role.owned_by_organisation)
        return

    # ---------------------------------------------------------------------
    @staticmethod
    def project_project_deduplicate(item):
        """ Import item de-duplication """

        db = current.db

        if item.id:
            return
        if item.tablename == "project_project" and \
            "name" in item.data:
            # Match project by name (all-lowercase)
            table = item.table
            name = item.data.name
            query = (table.name.lower() == name.lower())
            duplicate = db(query).select(table.id,
                                         limitby=(0, 1)).first()
            if duplicate:
                item.id = duplicate.id
                item.method = item.METHOD.UPDATE
        return

    # ---------------------------------------------------------------------
    @staticmethod
    def hfa_opts_represent(opt, row=None):
        """ Option representation """

        s3 = current.response.s3
        NONE = current.messages.NONE

        project_hfa_opts = s3.project_hfa_opts

        opts = opt
        if isinstance(opt, int):
            opts = [opt]
        elif not isinstance(opt, (list, tuple)):
            return NONE
        vals = [project_hfa_opts.get(o, NONE) for o in opts]
        return ", ".join(vals)

    # ---------------------------------------------------------------------
    @staticmethod
    def project_organisation_onvalidation(form, lead_role=None):
        """ Form validation """

        db = current.db
        s3 = current.response.s3

        otable = S3Model.table("project_organisation")

        if lead_role is None:
            lead_role = s3.project_organisation_lead_role

        project_id = form.vars.project_id
        organisation_id = form.vars.organisation_id
        if str(form.vars.role) == str(lead_role) and project_id:
            query = (otable.deleted != True) & \
                    (otable.project_id == project_id) & \
                    (otable.role == lead_role) & \
                    (otable.organisation_id != organisation_id)
            row = db(query).select(otable.id, limitby=(0, 1)).first()
            if row:
                form.errors.role = T("Lead Implementer for this project is already set, please choose another role.")
        return

    # ---------------------------------------------------------------------
    @staticmethod
    def project_organisation_deduplicate(item):
        """ Import item de-duplication """

        db = current.db

        if item.id:
            return
        if item.tablename == "project_organisation" and \
            "project_id" in item.data and \
            "organisation_id" in item.data:
            # Match project by org_id and project_id
            table = item.table
            project_id = item.data.project_id
            organisation_id = item.data.organisation_id
            query = (table.project_id == project_id) & \
                    (table.organisation_id == organisation_id)
            duplicate = db(query).select(table.id,
                                         limitby=(0, 1)).first()
            if duplicate:
                item.id = duplicate.id
                item.method = item.METHOD.UPDATE
        return

    # ---------------------------------------------------------------------
    @staticmethod
    def activity_type_comment(label):
        """ Re-usable field comment """

        auth = current.auth

        # @todo: should not use a group ID here => use a UUID!
        if auth.has_membership(auth.id_group(1)):
            return DIV(A(label,
                            _class="colorbox",
                            _href=URL(c="project", f="activity_type",
                                    args="create",
                                    vars=dict(format="popup")),
                            _target="top",
                            _title=label
                            )
                        )
        else:
            return None

    # ---------------------------------------------------------------------
    @staticmethod
    def project_activity_onaccept(form):
        """ Record creation post-processing """

        db = current.db
        settings = current.deployment_settings
        pca = settings.get_project_community_activity()

        if not pca:
           if "name" in form.vars and \
              form.vars.name and form.vars.location_id:
                table = S3Model.table("gis_location")
                query = (table.id == form.vars.location_id)
                row = db(query).select(table.id, table.level,
                                       limitby=(0, 1)).first()
                if row and not row.level:
                    row.update_record(name=form.vars.name)
        return

    # ---------------------------------------------------------------------
    @staticmethod
    def project_activity_deduplicate(item):
        """ Import item de-duplication """

        db = current.db
        settings = current.deployment_settings
        pca = settings.get_project_community_activity()

        if item.id:
            return
        if item.tablename != "project_activity":
            return
        table = item.table
        duplicate = None
        if pca:
           if "project_id" in item.data and \
              "location_id" in item.data:
                # Match activity by project_id and location_id
                project_id = item.data.project_id
                location_id = item.data.location_id
                query = (table.project_id == project_id) & \
                        (table.location_id == location_id)
                duplicate = db(query).select(table.id,
                                             limitby=(0, 1)).first()
        else:
           if "project_id" in item.data and "name" in item.data:
                # Match activity by project_id and name
                project_id = item.data.project_id
                name = item.data.name
                query = (table.project_id == project_id) & \
                        (table.name == name)
                duplicate = db(query).select(table.id,
                                             limitby=(0, 1)).first()
        if duplicate:
            item.id = duplicate.id
            item.method = item.METHOD.UPDATE
        return

    # ---------------------------------------------------------------------
    @staticmethod
    def beneficiary_type_represent(type_id, row=None):
        """ FK representation """

        db = current.db
        UNKNOWN_OPT = current.messages.UNKNOWN_OPT

        if isinstance(type_id, Row):
            if "name" in type_id:
                return type_id.name
            elif "id" in type_id:
                type_id = type_id.id
            else:
                return UNKNOWN_OPT

        bnf_type = S3Model.table("project_beneficiary_type")
        query = bnf_type.id == type_id
        row = db(query).select(bnf_type.name, limitby=(0, 1)).first()
        if row:
            return row.name
        else:
            return UNKNOWN_OPT

    # ---------------------------------------------------------------------
    @staticmethod
    def project_beneficiary_onaccept(form):
        """ Record creation post-processing """

        db = current.db

        btable = S3Model.table("project_beneficiary")
        atable = S3Model.table("project_activity")

        record_id = form.vars.id
        query = (btable.id == record_id) & \
                (atable.id == btable.activity_id)
        activity = db(query).select(atable.project_id,
                                    limitby=(0, 1)).first()
        if activity:
            db(btable.id == record_id).update(project_id=activity.project_id)
        return

    # ---------------------------------------------------------------------
    @staticmethod
    def project_beneficiary_deduplicate(item):
        """ Import item de-duplication """

        db = current.db

        if item.id:
            return
        if item.tablename == "project_beneficiary" and \
            "bnf_type" in item.data and \
            "activity_id" in item.data:
            # Match beneficiary by type and activity_id
            table = item.table
            bnf_type = item.data.bnf_type
            activity_id = item.data.activity_id
            query = (table.bnf_type == bnf_type) & \
                    (table.activity_id == activity_id)
            duplicate = db(query).select(table.id,
                                            limitby=(0, 1)).first()
            if duplicate:
                item.id = duplicate.id
                item.method = item.METHOD.UPDATE
        return

    # -------------------------------------------------------------------------
    @staticmethod
    def task_onvalidation(form):
        """ Task form validation """

        if str(form.vars.status) == "3" and not form.vars.pe_id:
            form.errors.pe_id = \
                T("Status 'assigned' requires the %(fieldname)s to not be blank") % \
                    dict(fieldname=db.project_task.pe_id.label)
        return

    # -------------------------------------------------------------------------
    @staticmethod
    def task_create_onaccept(form):
        """
            When a Task is created:
                create associated Link Tables
                ensure that it is owned by the Project Customer
        """

        db = current.db
        s3db = current.s3db
        session = current.session

        if session.s3.event:
            # Create a link between this Task & the active Event
            etable = s3db.event_task
            etable.insert(event_id=session.s3.event,
                          task_id=form.vars.id)

        # Find the associated Project
        ptable = db.project_project
        ltable = db.project_task_project
        query = (ltable.task_id == form.vars.id) & \
                (ltable.project_id == ptable.id)
        project = db(query).select(ptable.organisation_id,
                                   limitby=(0, 1)).first()
        if project:
            # Set Task to be owned by this Customer
            organisation_id = project.organisation_id
            otable = s3db.org_organisation
            query = (otable.id == organisation_id)
            role = db(query).select(otable.owned_by_organisation,
                                    limitby=(0, 1)).first()
            if role:
                table = s3db.project_task
                query = (table.id == form.vars.id)
                db(query).update(owned_by_organisation=role.owned_by_organisation)

        return

    # -------------------------------------------------------------------------
    @staticmethod
    def time_onaccept(form):
        """ When Time is logged, update the Task & Activity """

        db = current.db
        titable = db.project_time
        ttable = db.project_task
        atable = db.project_activity
        tatable = db.project_task_activity

        # Find the Task
        task_id = form.vars.task_id
        if not task_id:
            # Component Form
            query = (titable.id == form.vars.id)
            record = db(query).select(titable.task_id,
                                      limitby=(0, 1)).first()
            if record:
                task_id = record.task_id

        # Total the Hours Logged
        query = (titable.deleted == False) & \
                (titable.task_id == task_id)
        rows = db(query).select(titable.hours)
        hours = 0
        for row in rows:
            hours += row.hours
        
        # Update the Task
        query = (ttable.id == task_id)
        db(query).update(time_actual=hours)

        # Find the Activity
        query = (tatable.deleted == False) & \
                (tatable.task_id == task_id)
        activity = db(query).select(tatable.activity_id,
                                    limitby=(0, 1)).first()
        if activity:
            activity_id = activity.activity_id

            # Find all Tasks in this Activity
            query = (ttable.deleted == False) & \
                    (tatable.deleted == False) & \
                    (tatable.task_id == ttable.id) & \
                    (tatable.activity_id == activity_id)
            tasks = db(query).select(ttable.time_actual)

            # Total the Hours Logged
            hours = 0
            for task in tasks:
                hours += task.time_actual
            
            # Update the Activity
            query = (atable.id == activity_id)
            db(query).update(time_actual=hours)

        return

# =============================================================================
def project_rheader(r, tabs=[]):
    """ Project Resource Headers - used in Project & Budget modules """

    T = current.T
    db = current.db
    auth = current.auth
    s3 = current.response.s3
    settings = current.deployment_settings
    pca = settings.get_project_community_activity()

    rheader = None

    if r.representation == "html":
        rheader_tabs = s3_rheader_tabs(r, tabs)
        table = r.table
        record = r.record
        if record:
            if r.name == "project":
                rheader = DIV(TABLE(
                    TR(
                       TH("%s: " % table.name.label),
                       record.name
                      ),
                    TR(
                       TH("%s: " % table.organisation_id.label),
                       s3.org_organisation_represent(record.organisation_id)
                      ),
                    TR(
                       #TH("%s: " % table.countries_id.label),
                       #table.countries_id.represent(record.countries_id),
                       TH("%s: " % table.end_date.label),
                       record.end_date
                      ),
                    ), rheader_tabs)

            elif r.name == "activity":
                # @todo: integrate tabs?
                if pca:
                    tbl = TABLE(
                                TR(
                                   TH("%s: " % table.location_id.label),
                                   s3.gis_location_represent(record.location_id)
                                  )
                               )
                else:
                    tbl = TABLE(
                                TR(
                                   TH("%s: " % table.name.label),
                                   record.name
                                  )
                               )
                if record.project_id is not None:
                    tbl.append(TR(TH("%s: " % table.project_id.label),
                                  table.project_id.represent(record.project_id)))
                rheader = DIV(tbl, rheader_tabs)
            elif r.name == "task":
                tabs = [(T("Details"), None)]
                staff = auth.s3_has_role("STAFF")
                if staff:
                        (T("Time"), "time"),
                tabs.append((T("Comments"), "discuss"))
                tabs.append((T("Attachments"), "document"))
                #(T("Roles"), "job_role"),
                #(T("Assignments"), "human_resource"),
                #(T("Requests"), "req")

                rheader_tabs = s3_rheader_tabs(r, tabs)

                ctable = db.project_comment
                query = (ctable.deleted == False) & \
                        (ctable.task_id == r.id)
                comments = db(query).count()
                if comments:
                    comments = TR(
                                    TH("%s: " % T("Comments")),
                                    A(comments,
                                      _href=URL(args=[r.id, "discuss"]))
                                )
                else:
                    comments = ""

                rheader = DIV(TABLE(
                    TR(
                        TH("%s: " % table.name.label),
                        record.name,
                        #TH("%s: " % table.site_id.label),
                        #s3.org_site_represent(record.site_id),
                        ),
                    TR(
                        TH("%s: " % table.pe_id.label),
                        s3.pr_pentity_represent(record.pe_id,
                                                show_label=False),
                        #TH("%s: " % table.location_id.label),
                        #s3.gis_location_represent(record.location_id),
                        ),
                    TR(
                        TH("%s: " % table.description.label),
                        record.description
                        ),
                    TR(
                        TH("%s: " % table.time_estimated.label),
                        record.time_estimated,
                        ),
                    TR(
                        TH("%s: " % table.time_actual.label),
                        record.time_actual
                        ),
                    comments,
                    ), rheader_tabs)

    return rheader

# =============================================================================
class S3ProjectActivityVirtualfields:
    """ Virtual fields for the project_activity table """

    extra_fields = ["project_id", "location_id"]

    def organisation(self):
        """ Name of the lead organisation of the project """

        db = current.db
        s3 = current.response.s3

        otable = S3Model.table("org_organisation")
        ltable = S3Model.table("project_organisation")
        LEAD_ROLE = s3.project_organisation_lead_role
        query = (ltable.deleted != True) & \
                (ltable.project_id == self.project_activity.project_id) & \
                (ltable.role == LEAD_ROLE) & \
                (ltable.organisation_id == otable.id)
        org = db(query).select(otable.name,
                               limitby=(0, 1)).first()
        if org:
            return org.name
        else:
            return None

    def L0(self):
        parents = Storage()
        parents = current.gis.get_parent_per_level(parents,
                                                   self.project_activity.location_id,
                                                   ids=False,
                                                   names=True)
        if "L0" in parents:
            return parents["L0"]
        else:
            return None

    def L1(self):
        parents = Storage()
        parents = current.gis.get_parent_per_level(parents,
                                                   self.project_activity.location_id,
                                                   ids=False,
                                                   names=True)
        if "L1" in parents:
            return parents["L1"]
        else:
            return None

    def L2(self):
        parents = Storage()
        parents = current.gis.get_parent_per_level(parents,
                                                   self.project_activity.location_id,
                                                   ids=False,
                                                   names=True)
        if "L2" in parents:
            return parents["L2"]
        else:
            return None

    def L3(self):
        parents = Storage()
        parents = current.gis.get_parent_per_level(parents,
                                                   self.project_activity.location_id,
                                                   ids=False,
                                                   names=True)
        if "L3" in parents:
            return parents["L3"]
        else:
            return None

# =============================================================================
class S3ProjectTimeVirtualfields:
    """ Virtual fields for the project_time table """

    extra_fields = ["task_id", "person_id", "date"]

    def project(self):
        """
            Project associated with this time entry
            - used by the 'Project Income Allocation' report
        """

        db = current.db

        ptable = S3Model.table("project_project")
        ltable = S3Model.table("project_task_project")
        query = (ltable.deleted != True) & \
                (ltable.task_id == self.project_time.task_id) & \
                (ltable.project_id == ptable.id)
        project = db(query).select(ptable.name,
                                   limitby=(0, 1)).first()
        if project:
            return project.name
        else:
            return None

    def day(self):
        """
            Day of the last Week this time entry relates to
            - used by the 'Last Week's Work' report
        """

        T = current.T
        now = current.request.utcnow
        thisdate = self.project_time.date

        if not thisdate:
            return "-"

        week = datetime.timedelta(days=7)
        if thisdate < (now - week):
            # Ignore data older than the last week
            # - should already be filtered in controller anyway
            return "-"

        return thisdate.date().strftime("%d %B")

# END =========================================================================
