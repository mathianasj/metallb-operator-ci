#!/usr/bin/env python3
import yaml
import sys

csv_path = 'bundle/manifests/metallb-operator.clusterserviceversion.yaml'

with open(csv_path, 'r') as f:
    csv = yaml.safe_load(f)

# Find and patch the webhook-server container
for deploy in csv['spec']['install']['spec']['deployments']:
    if deploy['name'] == 'metallb-operator-webhook-server':
        for container in deploy['spec']['template']['spec']['containers']:
            if container['name'] == 'webhook-server':
                env = container.get('env', [])
                names = [e.get('name', '') for e in env]
                if 'METALLB_POD_NAME' not in names:
                    env.append({
                        'name': 'METALLB_POD_NAME',
                        'valueFrom': {'fieldRef': {'fieldPath': 'metadata.name'}}
                    })
                if 'OPERATOR_CONDITION_NAME' not in names:
                    env.append({
                        'name': 'OPERATOR_CONDITION_NAME',
                        'value': 'metallb-operator.v4.22.0'
                    })
                container['env'] = env
                if 'readinessProbe' in container:
                    del container['readinessProbe']
                    print(f"Removed readinessProbe from webhook-server container")
                if 'livenessProbe' in container:
                    del container['livenessProbe']
                    print(f"Removed livenessProbe from webhook-server container")
                print(f"Patched webhook-server container in deployment {deploy['name']}")
                break
        break

with open(csv_path, 'w') as f:
    yaml.dump(csv, f, default_flow_style=False)

print('Done patching CSV')
