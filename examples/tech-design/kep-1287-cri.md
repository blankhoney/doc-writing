# KEP-1287 容器原地更新：局部 CRI 契约（已核验局部来源·中文节译）

- **来源**：[KEP-1287 README](https://github.com/kubernetes/enhancements/blob/d47a8df46c8c26d6300fd30047520e397127805c/keps/sig-node/1287-in-place-update-pod-resources/README.md) 第 360–413 行 CRI Changes 一节，固定提交 `d47a8df46c8c26d6300fd30047520e397127805c`
- **许可**：Apache-2.0，与 KEP-753 共用[许可证副本](../licenses/kubernetes-enhancements-LICENSE.txt)；原始选段校验值与删节见 [SOURCES.md](../SOURCES.md#kep-1287)
- **取样**：只取局部 CRI 契约；未取 Resize Status 与新旧状态名混用的失败处理。这是演进稿的局部范围，不代表运行时已支持
- **未运行**：未运行集群、CRI 运行时或 NRI 插件

## CRI 变更

自 Kubernetes v1.20 起，CRI 通过 `UpdateContainerResources` API 支持容器原地调整资源，containerd 与 CRI-O 都已实现；`ContainerStatus` 消息的 `ContainerResources` 字段报告容器当前的资源配置。同一配置多次调用时，`UpdateContainerResources` 必须保持幂等。

从 Kubernetes v1.33 起，该调用的契约将更新为：运行时不应为了调整资源而故意重启容器。如果调整资源必须重启，运行时应当改为返回错误。仍可能存在触发重启的边界情况（见原文 Memory Limit Decreases 一节），因此这是尽力而为的要求，没有强制机制。

尽管 Pod 级 cgroup 目前由 Kubelet 管理，运行时可能需要在资源配置变化时被告知，例如该信息应传递给 NRI 插件。为此新增 `UpdatePodSandboxResources` API：

```proto
service RuntimeService {
  ...

  // UpdatePodSandboxResources synchronously updates the PodSandboxConfig with
  // the pod-level resource configuration. This method is called _after_ the
  // Kubelet reconfigures the pod-level cgroups.
  // This request is treated as best effort, and failure will not block the
  // Kubelet with proceeding with a resize.
  rpc UpdatePodSandboxResources(UpdatePodSandboxResourcesRequest) returns (UpdatePodSandboxResourcesResponse) {}
}

message UpdatePodSandboxResourcesRequest {
    // ID of the PodSandbox to update.
    string pod_sandbox_id = 1;

    // Optional overhead represents the overheads associated with this sandbox
    LinuxContainerResources overhead = 2;
    // Optional resources represents the sum of container resources for this sandbox
    LinuxContainerResources resources = 3;
}

message UpdatePodSandboxResourcesResponse {}
```

Kubelet 会在重新配置 Pod 级 cgroup 之后调用 `UpdatePodSandboxResources`。该顺序与创建 Pod 时一致：Kubelet 先配置 Pod 级 cgroup，再调用 `RunPodSandbox`。

目前 Kubelet 把该调用视为尽力而为：出现错误时只记录日志，其余忽略并继续调整。

注意：此处不包含 Windows 资源，因为 `WindowsPodSandboxConfig` 中没有这些资源。
