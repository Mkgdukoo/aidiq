<?xml version="1.0"?>
<xsl:stylesheet
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

    <!-- **********************************************************************
         Project Tasks (Requirements) - CSV Import Stylesheet

         2012-01-05 / Fran Boon <fran[AT]aidiq[DOT]com>

         CSV column...........Format..........Content

         Customer.............string..........Project Customer
         Project..............string..........Project Name
         Activity.............string..........Activity
         Activity Type........string..........Activity Type
         Name.................string..........Task short description
         Description..........string..........Task detailed description
         Date.................string..........Task created_on
         Author...............string..........Task created_by
         Source...............string..........Task source
         Assigned.............string..........Person Initials
         Priority.............string..........Task priority
         Status...............string..........Task status
         Comments.............string..........Task comment

    *********************************************************************** -->

    <xsl:output method="xml"/>

    <xsl:include href="../../xml/commons.xsl"/>

    <xsl:key name="customers" match="row" use="col[@field='Customer']"/>
    <xsl:key name="projects" match="row" use="col[@field='Project']"/>
    <xsl:key name="activity types" match="row" use="col[@field='Activity Type']"/>
    <xsl:key name="activities" match="row" use="col[@field='Activity']"/>
    <xsl:key name="assignees" match="row" use="col[@field='Assigned']"/>

    <!-- ****************************************************************** -->
    <xsl:template match="/">
        <s3xml>
            <!-- Customers -->
            <xsl:for-each select="//row[generate-id(.)=generate-id(key('customers',
                                                                   col[@field='Customer'])[1])]">
                <xsl:call-template name="Organisation"/>
            </xsl:for-each>

            <!-- Projects -->
            <xsl:for-each select="//row[generate-id(.)=generate-id(key('projects',
                                                                   col[@field='Project'])[1])]">
                <xsl:call-template name="Project"/>
            </xsl:for-each>

            <!-- Activity Types -->
            <xsl:for-each select="//row[generate-id(.)=generate-id(key('activity types',
                                                                   col[@field='Activity Type'])[1])]">
                <xsl:call-template name="ActivityType"/>
            </xsl:for-each>

            <!-- Activities -->
            <xsl:for-each select="//row[generate-id(.)=generate-id(key('activities',
                                                                   col[@field='Activity'])[1])]">
                <xsl:call-template name="Activity"/>
            </xsl:for-each>

            <!-- Assignees -->
            <xsl:for-each select="//row[generate-id(.)=generate-id(key('assignees',
                                                                   col[@field='Assigned'])[1])]">
                <xsl:call-template name="Person"/>
            </xsl:for-each>

            <!-- Tasks -->
            <xsl:apply-templates select="./table/row"/>
        </s3xml>
    </xsl:template>

    <!-- ****************************************************************** -->
    <xsl:template match="row">
        <xsl:variable name="ProjectName" select="col[@field='Project']/text()"/>
        <xsl:variable name="ActivityName" select="col[@field='Activity']/text()"/>
        <xsl:variable name="Task" select="col[@field='Short Description']/text()"/>
        <xsl:variable name="Date" select="col[@field='Date']/text()"/>
        <xsl:variable name="Author" select="col[@field='Raised By']/text()"/>
        <xsl:variable name="Assignee" select="col[@field='Assigned']/text()"/>
        <xsl:variable name="Priority" select="col[@field='Priority']/text()"/>

        <resource name="project_task">
            <xsl:attribute name="created_on">
                <xsl:value-of select="$Date"/>
            </xsl:attribute>
            <xsl:attribute name="modified_on">
                <xsl:value-of select="$Date"/>
            </xsl:attribute>
            <xsl:attribute name="created_by">
                <xsl:value-of select="$Author"/>
            </xsl:attribute>
            <xsl:attribute name="modified_by">
                <xsl:value-of select="$Author"/>
            </xsl:attribute>
            <data field="name"><xsl:value-of select="$Task"/></data>
            <data field="description"><xsl:value-of select="col[@field='Detailed Description']/text()"/></data>
            <data field="source"><xsl:value-of select="col[@field='Source']/text()"/></data>
            <xsl:choose>
                <xsl:when test="$Priority='Urgent'">
                    <data field="priority">1</data>
                </xsl:when>
                <xsl:when test="$Priority='High'">
                    <data field="priority">2</data>
                </xsl:when>
                <xsl:when test="$Priority='Medium'">
                    <data field="priority">3</data>
                </xsl:when>
                <xsl:when test="$Priority='Normal'">
                    <data field="priority">3</data>
                </xsl:when>
                <xsl:when test="$Priority='Low'">
                    <data field="priority">4</data>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:choose>
                        <xsl:when test="$Priority!=''">
                            <!-- Assume an integer to just copy straight across -->
                            <data field="priority"><xsl:value-of select="$Priority"/></data>
                        </xsl:when>
                        <xsl:otherwise>
                            <!-- Assign a priority of 'Normal' -->
                            <data field="priority">3</data>
                        </xsl:otherwise>
                    </xsl:choose>
                </xsl:otherwise>
            </xsl:choose>
            <xsl:choose>
                <xsl:when test="col[@field='Status']='Draft'">
                    <data field="status">1</data>
                </xsl:when>
                <xsl:when test="col[@field='Status']='New'">
                    <data field="status">2</data>
                </xsl:when>
                <xsl:when test="col[@field='Status']='Assigned'">
                    <data field="status">3</data>
                </xsl:when>
                <xsl:when test="col[@field='Status']='On Hold'">
                    <data field="status">4</data>
                </xsl:when>
                <xsl:when test="col[@field='Status']='Feedback'">
                    <data field="status">5</data>
                </xsl:when>
                <xsl:when test="col[@field='Status']='Cancelled'">
                    <data field="status">6</data>
                </xsl:when>
                <xsl:when test="col[@field='Status']='Blocked'">
                    <data field="status">7</data>
                </xsl:when>
                <xsl:when test="col[@field='Status']='Completed'">
                    <data field="status">8</data>
                </xsl:when>
                <xsl:when test="col[@field='Status']='Verified'">
                    <data field="status">9</data>
                </xsl:when>
                <xsl:when test="col[@field='Status']='Closed'">
                    <!-- Completed -->
                    <data field="status">8</data>
                </xsl:when>
                <xsl:otherwise>
                    <!-- Open -->
                    <xsl:choose>
                        <xsl:when test="col[@field='Assigned']!=''">
                            <!-- Assigned -->
                            <data field="status">3</data>
                        </xsl:when>
                        <xsl:otherwise>
                            <!-- New -->
                            <data field="status">2</data>
                        </xsl:otherwise>
                    </xsl:choose>
                </xsl:otherwise>
            </xsl:choose>
            <!-- Link to Assignee -->
            <reference field="pe_id" resource="pr_person">
                <xsl:attribute name="tuid">
                    <xsl:value-of select="$Assignee"/>
                </xsl:attribute>
            </reference>
            <!-- Link to Project -->
            <resource name="project_task_project">
                <reference field="project_id" resource="project_project">
                    <xsl:attribute name="tuid">
                        <xsl:value-of select="$ProjectName"/>
                    </xsl:attribute>
                </reference>
            </resource>
            <!-- Link to Activity -->
            <resource name="project_task_activity">
                <reference field="activity_id" resource="project_activity">
                    <xsl:attribute name="tuid">
                        <xsl:value-of select="$ActivityName"/>
                    </xsl:attribute>
                </reference>
            </resource>
            <!-- Comment -->
            <xsl:if test="col[@field='Comments']/text()!=''">
                <resource name="project_comment">
                    <data field="body"><xsl:value-of select="col[@field='Comments']/text()"/></data>
                </resource>
            </xsl:if>
        </resource>

    </xsl:template>

    <!-- ****************************************************************** -->
    <xsl:template name="Organisation">
        <xsl:variable name="OrganisationName" select="col[@field='Customer']/text()"/>

        <resource name="org_organisation">
            <xsl:attribute name="tuid">
                <xsl:value-of select="$OrganisationName"/>
            </xsl:attribute>
            <data field="name"><xsl:value-of select="$OrganisationName"/></data>
        </resource>

    </xsl:template>

    <!-- ****************************************************************** -->
    <xsl:template name="Project">
        <xsl:variable name="ProjectName" select="col[@field='Project']/text()"/>
        <xsl:variable name="OrganisationName" select="col[@field='Customer']/text()"/>

        <resource name="project_project">
            <xsl:attribute name="tuid">
                <xsl:value-of select="$ProjectName"/>
            </xsl:attribute>
            <data field="name"><xsl:value-of select="$ProjectName"/></data>
            <!-- Link to Customer -->
            <reference field="organisation_id" resource="org_organisation">
                <xsl:attribute name="tuid">
                    <xsl:value-of select="$OrganisationName"/>
                </xsl:attribute>
            </reference>
        </resource>

    </xsl:template>

    <!-- ****************************************************************** -->
    <xsl:template name="ActivityType">
        <xsl:variable name="ActivityType" select="col[@field='Activity Type']/text()"/>

        <resource name="project_activity_type">
            <xsl:attribute name="tuid">
                <xsl:value-of select="$ActivityType"/>
            </xsl:attribute>
            <data field="name"><xsl:value-of select="$ActivityType"/></data>
        </resource>

    </xsl:template>

    <!-- ****************************************************************** -->
    <xsl:template name="Activity">
        <xsl:variable name="ProjectName" select="col[@field='Project']/text()"/>
        <xsl:variable name="ActivityName" select="col[@field='Activity']/text()"/>
        <xsl:variable name="ActivityType" select="col[@field='Activity Type']/text()"/>

        <resource name="project_activity">
            <xsl:attribute name="tuid">
                <xsl:value-of select="$ActivityName"/>
            </xsl:attribute>
            <data field="name"><xsl:value-of select="$ActivityName"/></data>
            <!-- Link to Project -->
            <reference field="project_id" resource="project_project">
                <xsl:attribute name="tuid">
                    <xsl:value-of select="$ProjectName"/>
                </xsl:attribute>
            </reference>
            <!-- Link to Type -->
            <reference field="activity_type_id" resource="project_activity_type">
                <xsl:attribute name="tuid">
                    <xsl:value-of select="$ActivityType"/>
                </xsl:attribute>
            </reference>
        </resource>

    </xsl:template>

    <!-- ****************************************************************** -->
    <xsl:template name="Person">
        <xsl:variable name="Assignee" select="col[@field='Assigned']/text()"/>

        <resource name="pr_person">
            <xsl:attribute name="tuid">
                <xsl:value-of select="$Assignee"/>
            </xsl:attribute>
            <data field="initials"><xsl:value-of select="$Assignee"/></data>
        </resource>

    </xsl:template>

    <!-- ****************************************************************** -->

</xsl:stylesheet>