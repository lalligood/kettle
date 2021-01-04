# Pentaho Notes

## Pentaho Data Integration Installation on Mac OSX

### Download & unzip PDI

1. [Download the latest version](https://sourceforge.net/projects/pentaho/files/Data%20Integration/).
2. Unzip the downloaded file.
3. Copy `data-integration` folder to `/Applications` directory.
4. In *Finder* application, navigate to `data-integration` folder in **Applications**.
5. "Un-quarantine" the `.app` file by opening a terminal & running this command:

    `xattr -dr com.apple.quarantine /Applications/data-integration/Data\ Integration.app`

6. Allocate more RAM to Pentaho Data Integration application.
    1. Open `/Applications/data-integration/spoon.sh` in text editor of choice.
    2. Find & change the following line (~ line 240)

        `PENTAHO_DI_JAVA_OPTIONS="-Xms1024m -Xmx2048m -XX:MaxPermSize=256m"`

        to (assuming 16GB RAM on workstation)

        `PENTAHO_DI_JAVA_OPTIONS="-Xms2g -Xmx8g -XX:MaxPermSize=256m"`

    3. Save changes & exit.

### Download & install Java

[Follow these instructions for installing OpenJDK8](https://installvirtual.com/install-openjdk-8-on-mac-using-brew-adoptopenjdk/).

### Configure application & copy in `kettle.properties` file

Get `kettle.properties` file from coworker & copy to `/Applications/data-integration` directory.

### Download MySQL Connector

1. [Open this webpage](https://dev.mysql.com/downloads/connector/j/).
2. Under *Select Operating System*, click on the drop-down list & select
    **Platform Independent**.
3. Click on **Download** button beside the ZIP Archive.
4. Click on **No thanks, just start my download** link.
5. Unzip the file & copy `mysql-connector-java-X.YY.ZZ.jar` to
    `/Applications/data-integrations/lib`.
    * Note: Where `X.YY.ZZ` matches the version of MySQL you are running.

## Plugin Installation

There are a couple plugins that need to be installed for some tasks within transformations.

### Top/Bottom/First/Last Filter

This filter is a plugin installed through the Pentaho Marketplace.

To install the filter plugin:

1. Launch Pentaho Data Integration (PDI) application.
2. Click on **Tools** -> **Marketplace**.
3. In the search field, type `Top /`
    * It should automatically filter your results as you type so there's no need to type
        out the entire name.
4. Click on the **Install** button.
5. Restart PDI.

The following transformations require the filter in order to run:

```bash
src/transformation/dbo_timestamp.ktr
src/transformation/add_group_id_to_question_closure.ktr
```

### Web Scraping

The following transformations contain Jsoup for doing some web scraping work:

```bash
src/transformation/dbo_referral_activity_financial_assistance.ktr
src/transformation/dbo_dw_rm_financial_assistance_history.ktr
src/transformation/stm2_response_select.ktr
src/transformation/dbo_activity_response.ktr
src/transformation/stm2_answer.ktr
src/transformation/dbo_answer_inc.ktr
src/transformation/stm2_question.ktr
src/transformation/dbo_question.ktr
src/transformation/dbo_answer.ktr
```

* [Jsoup error explainer](https://stackoverflow.com/questions/50402278/how-to-parse-html-files-with-pentaho)
    which also includes where/how to install
* [Jsoup download](https://jsoup.org/download)

```bash
mv ~/Downloads/jsoup-X.YY.Z.jar /Applications/data-integration/lib/
```
