{{- define "home-essentials.fullname" -}}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "home-essentials.name" -}}
{{- .Chart.Name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "home-essentials.labels" -}}
app: {{ include "home-essentials.name" . }}
release: {{ .Release.Name }}
{{- end }}

{{- define "home-essentials.selectorLabels" -}}
app: {{ include "home-essentials.name" . }}
release: {{ .Release.Name }}
{{- end }}
