import { useEffect, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Navigate, Route, Routes, useLocation, useNavigate } from "react-router-dom";
import { api } from "./api/client";
import { AppShell } from "./layouts/AppShell";
import { DashboardPage } from "./pages/DashboardPage";
import { DocumentsPage } from "./pages/DocumentsPage";
import { HelpPage } from "./pages/HelpPage";
import { LoginPage } from "./pages/LoginPage";
import { ReviewsPage } from "./pages/ReviewsPage";
import { SearchPage } from "./pages/SearchPage";

function ReviewerOnly({ user, children }) {
  if (!["reviewer", "admin"].includes(user?.role)) {
    return <Navigate to="/dashboard" replace />;
  }
  return children;
}

export default function App() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const location = useLocation();

  const [booting, setBooting] = useState(true);
  const [currentUser, setCurrentUser] = useState(null);
  const [notice, setNotice] = useState("Sign in with one of the demo accounts to start the workflow.");
  const [uploadProgress, setUploadProgress] = useState(0);
  const [searchResults, setSearchResults] = useState([]);

  useEffect(() => {
    async function bootstrap() {
      try {
        const session = await api.getSession();
        if (session?.authenticated) {
          setCurrentUser(session.user);
          setNotice(`Welcome back, ${session.user.display_name}.`);
          if (location.pathname === "/" || location.pathname === "/login") {
            navigate("/dashboard", { replace: true });
          }
        }
      } catch {
        setCurrentUser(null);
      } finally {
        setBooting(false);
      }
    }
    bootstrap();
  }, [location.pathname, navigate]);

  const dashboardQuery = useQuery({
    queryKey: ["dashboard"],
    queryFn: api.getDashboard,
    enabled: Boolean(currentUser),
    refetchInterval: 10_000,
  });

  const documentsQuery = useQuery({
    queryKey: ["documents"],
    queryFn: api.getDocuments,
    enabled: Boolean(currentUser),
    refetchInterval: 10_000,
  });

  const reviewsQuery = useQuery({
    queryKey: ["reviews"],
    queryFn: api.getReviews,
    enabled: Boolean(currentUser && ["reviewer", "admin"].includes(currentUser.role)),
    refetchInterval: 10_000,
  });

  const uploadMutation = useMutation({
    mutationFn: async ({ file, formState }) => {
      const uploadTicket = await api.requestUploadUrl({
        file_name: file.name,
        mime_type: file.type || "application/pdf",
      });

      await api.uploadToPresignedUrl(uploadTicket.upload_url, file, setUploadProgress);

      const finalizePayload = new FormData();
      Object.entries(formState).forEach(([key, value]) => finalizePayload.append(key, value));
      finalizePayload.append("file_name", file.name);
      finalizePayload.append("mime_type", file.type || "application/pdf");
      finalizePayload.append("minio_object_name", uploadTicket.object_name);
      finalizePayload.append("uploaded_via_presigned", "true");

      return api.uploadDocument(finalizePayload);
    },
    onMutate: () => setUploadProgress(0),
    onSuccess: () => {
      setNotice("Document processed successfully.");
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      queryClient.invalidateQueries({ queryKey: ["documents"] });
      queryClient.invalidateQueries({ queryKey: ["reviews"] });
      navigate("/documents");
    },
    onError: (error) => {
      setNotice(`Process document failed: ${error.message || "Unknown error"}`);
    },
    onSettled: () => {
      setTimeout(() => setUploadProgress(0), 500);
    },
  });

  const reviewDecisionMutation = useMutation({
    mutationFn: async ({ reviewId, documentId, decision, reviewer_feedback, corrected_fields }) => {
      const payload = { decision, reviewer_feedback, corrected_fields };
      if (reviewId) {
        return api.submitReviewByReviewId(reviewId, payload);
      }
      return api.submitReviewByDocument(documentId, { decision, comment: reviewer_feedback });
    },
    onSuccess: (_, variables) => {
      setNotice(`Review ${variables.decision} recorded for ${variables.documentId}.`);
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      queryClient.invalidateQueries({ queryKey: ["documents"] });
      queryClient.invalidateQueries({ queryKey: ["reviews"] });
    },
    onError: (error) => {
      setNotice(`Review action failed: ${error.message || "Unknown error"}`);
    },
  });

  const searchMutation = useMutation({
    mutationFn: (query) => api.searchDocuments(query, 20),
    onSuccess: (data) => {
      setSearchResults(data || []);
      setNotice(`Loaded ${(data || []).length} result(s).`);
    },
    onError: (error) => {
      setNotice(`Search failed: ${error.message || "Unknown error"}`);
    },
  });

  const handleLogin = async (credentials) => {
    const session = await api.login(credentials);
    setCurrentUser(session.user);
    setNotice(`Signed in as ${session.user.display_name}.`);
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: ["dashboard"] }),
      queryClient.invalidateQueries({ queryKey: ["documents"] }),
      queryClient.invalidateQueries({ queryKey: ["reviews"] }),
    ]);
    navigate("/dashboard", { replace: true });
  };

  const handleLogout = async () => {
    await api.logout();
    setCurrentUser(null);
    setSearchResults([]);
    queryClient.clear();
    setNotice("You have been logged out.");
    navigate("/login", { replace: true });
  };

  const topbar = useMemo(
    () => (
      <div className="mb-4 flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">B2C Operations</p>
          <h2 className="font-serif text-3xl">Agentic Document Intelligence</h2>
        </div>
        <div className="max-w-2xl rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm text-slate-600 shadow-sm">
          {notice}
        </div>
      </div>
    ),
    [notice]
  );

  if (booting) {
    return <div className="grid min-h-screen place-items-center text-slate-600">Initializing session...</div>;
  }

  if (!currentUser) {
    return (
      <Routes>
        <Route path="*" element={<LoginPage onLogin={handleLogin} notice={notice} />} />
      </Routes>
    );
  }

  return (
    <AppShell currentUser={currentUser} onLogout={handleLogout}>
      {topbar}
      <Routes>
        <Route
          path="/dashboard"
          element={<DashboardPage dashboard={dashboardQuery.data} loading={dashboardQuery.isFetching} onSelectDocument={() => navigate("/documents")} />}
        />
        <Route
          path="/documents"
          element={
            <DocumentsPage
              currentUser={currentUser}
              documents={documentsQuery.data || []}
              onUpload={(payload) => uploadMutation.mutateAsync(payload)}
              uploadProgress={uploadProgress}
              uploading={uploadMutation.isPending}
              onSelectDocument={() => {}}
            />
          }
        />
        <Route
          path="/reviews"
          element={
            <ReviewerOnly user={currentUser}>
              <ReviewsPage
                reviews={reviewsQuery.data || []}
                onDecision={(payload) => reviewDecisionMutation.mutateAsync(payload)}
                decisionInFlight={reviewDecisionMutation.isPending}
              />
            </ReviewerOnly>
          }
        />
        <Route
          path="/search"
          element={
            <SearchPage
              searchResults={searchResults}
              onSearch={(query) => searchMutation.mutateAsync(query)}
              searching={searchMutation.isPending}
              onSelectDocument={() => navigate("/documents")}
            />
          }
        />
        <Route path="/help" element={<HelpPage />} />
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/login" element={<Navigate to="/dashboard" replace />} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </AppShell>
  );
}
