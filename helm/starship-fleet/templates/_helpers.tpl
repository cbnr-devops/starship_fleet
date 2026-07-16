{{- define "starship-fleet.imageTagForSlot" -}}
{{- $root := index . 0 -}}
{{- $slot := index . 1 -}}
{{- if and $root.Values.blueGreen.enabled $slot -}}
{{- $slotTag := index $root.Values.blueGreen.slots $slot "imageTag" -}}
{{- if $slotTag -}}
{{- $slotTag -}}
{{- else -}}
{{- $root.Values.image.tag -}}
{{- end -}}
{{- else -}}
{{- $root.Values.image.tag -}}
{{- end -}}
{{- end -}}

{{- define "starship-fleet.container" -}}
- name: starship-fleet
  image: "{{ .Values.image.repository }}:{{ include "starship-fleet.imageTagForSlot" (list . .slot) }}"
  imagePullPolicy: {{ .Values.image.pullPolicy }}
  ports:
    - containerPort: 8000
  startupProbe:
    httpGet:
      path: /live
      port: 8000
    failureThreshold: 30
    periodSeconds: 5
  readinessProbe:
    httpGet:
      path: /ready
      port: 8000
    initialDelaySeconds: 5
    periodSeconds: 10
    timeoutSeconds: 2
    failureThreshold: 3
  livenessProbe:
    httpGet:
      path: /live
      port: 8000
    initialDelaySeconds: 15
    periodSeconds: 20
    timeoutSeconds: 2
    failureThreshold: 3
  env:
    - name: POSTGRES_USER
      valueFrom:
        secretKeyRef:
          name: postgres-secret
          key: POSTGRES_USER
    - name: POSTGRES_PASSWORD
      valueFrom:
        secretKeyRef:
          name: postgres-secret
          key: POSTGRES_PASSWORD
    - name: POSTGRES_HOST
      valueFrom:
        secretKeyRef:
          name: postgres-secret
          key: POSTGRES_HOST
  resources:
    {{- toYaml .Values.resources | nindent 4 }}
{{- end -}}
