from jinja2 import Template

presentation_template = Template('''{% autoescape false %}<pres:item>
    <pres:version>1.11</pres:version>
    <pres:entityUri>{{ uri }}</pres:entityUri>
    <pres:type>objekt</pres:type>
    <pres:id>{{ id }}</pres:id>
    <pres:idLabel>{{ id }}</pres:idLabel>
    <pres:itemLabel>{% autoescape true %}{{ label }}{% endautoescape %}</pres:itemLabel>
    {% if description %}<pres:description>{% autoescape true %}{{ description }}{% endautoescape %}</pres:description>{% endif %}
    {% if image %}
    <pres:image>
        <pres:src>{{ image['src'] }}</pres:src>
        {% if image['byline'] %}<pres:byline>{% autoescape true %}{{ image['byline'] }}{% endautoescape %}</pres:byline>{% endif %}
        {% if image['copyright'] %}<pres:copyright>{% autoescape true %}{{ image['copyright'] }}{% endautoescape %}</pres:copyright>{% endif %}
        <pres:mediaLicense>{{ image['license'] }}</pres:mediaLicense>
    </pres:image>
    {% endif %}
    <pres:representations>
        <pres:representation format="HTML">{{ html }}</pres:representation>
        <pres:representation format="RDF">{{ uri }}</pres:representation>
        <pres:representation format="presentation">{{ xml }}</pres:representation>
    </pres:representations>
    <pres:organization>{{ org }}</pres:organization>
    <pres:organizationShort>{{ org_short }}</pres:organizationShort>
    <pres:service>{{ service }}</pres:service>
    <pres:dataQuality>rådata</pres:dataQuality>
</pres:item>{% endautoescape %}''')
