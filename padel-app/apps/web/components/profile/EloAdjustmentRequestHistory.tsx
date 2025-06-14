"use client";

import { EloAdjustmentRequest } from "@/lib/types";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@workspace/ui/components/table";
import { Badge } from "@workspace/ui/components/badge";

interface EloAdjustmentRequestHistoryProps {
  requests: EloAdjustmentRequest[];
  loading: boolean;
}

export const EloAdjustmentRequestHistory = ({ requests, loading }: EloAdjustmentRequestHistoryProps) => {
  const canMakeRequest = () => {
    if (requests.some((req) => req.status === "pending")) {
      return false;
    }
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
    const recentRequest = requests.find(
      (req) => new Date(req.created_at) > thirtyDaysAgo
    );
    return !recentRequest;
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <h2 className="text-xl font-bold mb-4">ELO Adjustment Request History</h2>
      {!canMakeRequest() && (
        <p className="text-sm text-yellow-500 mb-4">
          You cannot make a new ELO adjustment request at this time. You either
          have a pending request or have made a request in the last 30 days.
        </p>
      )}
      {requests.length === 0 ? (
        <p>You have no ELO adjustment requests.</p>
      ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Date</TableHead>
              <TableHead>Requested Rating</TableHead>
              <TableHead>Reason</TableHead>
              <TableHead>Status</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {requests.map((request) => (
              <TableRow key={request.id}>
                <TableCell>
                  {new Date(request.created_at).toLocaleDateString()}
                </TableCell>
                <TableCell>{request.requested_rating.toFixed(1)}</TableCell>
                <TableCell>{request.reason}</TableCell>
                <TableCell>
                  <Badge
                    variant={
                      request.status === "approved"
                        ? "default"
                        : request.status === "rejected"
                        ? "destructive"
                        : "outline"
                    }
                  >
                    {request.status}
                  </Badge>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}
    </div>
  );
}; 