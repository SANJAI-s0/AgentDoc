lse "normaustomer") eload.get("vip_cy="high" if payrit        prio      s,
  tus=ingestion_statu,
                staurls", [])get("file_s=payload.         file_url      cksum", ""),
 ad.get("che   checksum=paylo
             ,count=page_count       page_         me_type,
  mime_type=mi           ),
   e", "unknown"file_namt("payload.geile_name= f
               , ""),storage_path"th=payload.get("e_pa  storag            web"),
  e_channel", "get("sourcayload. source_channel=p  ,
             mous")nyid", "anouser_("id=payload.get              user_
  ent_id,documocument_id=  d          ionOutput(
    on=Ingest     ingestiid,
       d=document_      document_i  tate(
    flowS    state = Work
    ejected"
_status = "r            workflowted":
ejection_status == "rd"
        if ingesd else "completeuirereview_reqg_review" if us = "pendin  workflow_statage
       # Audit st   )

           ting_reason],
  reasons=[rou           "complete",
 _required elsean" if review="await_humt_action nexdback=None,
              reviewer_feepleted",
         uired else "comeview_reqhuman" if r"await_  review_status=       a_minutes,
   inutes=sl   due_in_m",
         .th correctionsove/reject wiand apprrce document racted fields against sous="Review ext  instruction    ions",
      e "operat" els= "fraud_reviewstination_queue =deteam="fraud" if       assigned_required,
      ired=review_       review_requent_id.split('_')[-1]}",
     "rev_{documid=f review_  d,
         ocument_i        document_id=dOutput(
           review_output = Reviewon"}
 l_review", "exceptin in {"manuaactiored = routing_next_  review_requi ReviewOutput
      mporthemas i        from .scw preparation
     # Revie     )

   son],
       routing_rea             reasons=[al_review",
   ction="manu              next_aTrue,
  uman_review=ires_h              requit evidence.",
  st queue with full audte to specialiresolution_strategy="Rou                edium",
ore > 0.75 else "m"high" if risk_scation_level=       escal   ation.",
      supporting clarificr and request alate to reviewe     suggested_fix="Esc      lity",
     low_qua else "_type="suspected_fraud" if risk_score > 0.75   exceptioncument_id,
                document_id=doxceptionOutput(
                    exception_output = Ew":
     l_revieess_next == "manuaption" or preproc"excext_action ==     if routing_nexception_output = None
    put
        e import ExceptionOut  from .schemasing
      xception handl
        # Enutes = 30
w"
            sla_miual_revie_action = "man_nextng routi          ."
  to human reviewroutingce threshold unmet; ent or confiden "Issues pres         routing_reason =  rations"
 d_to = "ope          assignete_to_review"
  = "rou       next_step review"
       destination_queue = "operations_s_review:
          if need      el_minutes = 20
         sla
     tion = "exception"       routing_next_acalation."
     res escgh risk score requin = "Hirouting_reasofraud"
                assigned_to = "      alate"
  step = "esc      next_
      raud_review"ation_queue = "f destin  .75:
         _score > 0s = 5

        if risk        sla_minute= "complete"
ext_action routing_nsing."
        rough procesthfied for straight-ds satisdation threshol_reason = "Vali   routingation"
     autom    assigned_to = "pprove"
            next_step = "aeue = "auto_approve"
e
        destination_qu      # Routing stagds_review else "route"

  l_review" if nee   validation_next = "manua "approved"
     eeds_review elsereview" if nion_overall = "needs_ False)
        validat"force_review",ssues) or payload.get(_review = bool(i

        needs )
            )         h",
      ="higseverity                    d.",
eeded automation thresholscore exc   message="Risk arning",
                 "w               status=hold",
     ="risk_thresheck_name                 c ValidationCheck(
                 sues.append(
        is, 0.6):
     y.get("risk_threshold"ore > policf risk_sc     )

        i       )
               y="high",
               severit,
      sing_fields)}"ds: {', '.join(mis message=f"Missing fiel             failed",
      s="         statu          s",
 red_fieldrequi check_name="missing_     Check(
              alidation             Vssues.append(
   elds:
            i missing_fi
        if else 0.0
_mapp) if confidenceence_ma) / len(confid_map.values()encenf = sum(confid    avg_co.95), 4)
    _penalty, 0_penalty + qualityty + missingfidence_penalenalty + con.12 + handwritten_pin(0_score = round(m risk
       e 0.0ty_score < 0.7 elsage_qualialty = 0.14 if im  quality_pen.48)
      12, 0lds) * 0.len(missing_fiepenalty = min(        missing_ else 0.0
 0.8518 if class_conf <ce_penalty = 0.confiden
        en_form" else 0.0 "handwritte ==_typ12 if docdwritten_penalty = 0.       )
        )

        han     s else "low",
missing_fieldy="high" if      severit    .",
       ds extractedeld filse "All requireissing_fields eted." if md fields detecg requireissin    message="M         "passed",
   issing_fields else if mus="failed"     stat         fields",
   ="required_eck_name                chionCheck(
       Validat.append(
     "]
        validation_checksng_fieldsn_bundle["missilds = extractio missing_fie     = []
   = []
        issuesation_checks 
        validstage
        # Validation utput.")
m extracted ofrod fields are missing me requireappend("Soextraction_reasons."]:
            ssing_fields_bundle["mion if extractidate"
       "valiion_next = ]
        extractolicies." structured field pgnal andction using OCR siasons = ["Hybrid extraxtraction_re  )

        e                       )
 CR text.",
  rom O-based extraction f      evidence="Pattern    _page=1,
               source               me, 0.45)),
_nance_map.get(fielddence=float(confide confi                r None,
   lue=value o          vad_name,
          ame=fielld_n              fieion(
          FieldExtract         .append(
         field_models      
t(field_name)ructured_fields.ge       value = std_fields:
     ame in require  for field_n_models = []
              fieldidence_map"]

_bundle["confdence_map = extraction        confifields"]
"structured_dle[unextraction_bd_fields =    structureequired_fields)
     w_text, doc_type, ractor.extract(ra = field_extrn_bundle      extractiods", [])

  t("required_fiel = policy.gerequired_fields  
      PES else "invoice") SUPPORTED_TYtype if doc_type inpolicy_tool.run(doc_   policy = self.ge
     tion sta     # Extrac = "extract"

           class_next  else:
    d.")
      .85 thresholence below 0onfid cpend("Classifications.ap   class_reason
         l_review" = "manuaext    class_n5:
        f class_conf < 0.8l_review"
        elixt = "manua         class_ne:
   n"e == "unknow
        if doc_typayload, raw_text)
ent(pself._classify_documass_reasons = , clgorys_conf, cateoc_type, clas       dication stage
 lassifing.")

        # Ccess human preprold and needsquality is below threshomage pend("Iprocess_reasons.ap       pre  ":
   _reviewanualcess_next == "m"]
        if preproold 0.7.ty threshth qualisessed wiOCR readiness asns = ["reprocess_reaso p"
       anual_review.7 else "meprocess_next = "classify" if image_quality_score >= 0       prore - 0.05)

 _sc, image_quality0.72re = max(_sco       image_quality_count > 2:
            if pageage_quality_score = 0.68
             im_hint") or ""):
ocument_typein (payload.get("dwritten"    if "hand 0.82
     age_quality_score =     imessing stage
     # Preproc]

      _count + 1)
        page range(1, or idx in
            f          )   else 0.75,
0.9 if idx == 1 confidence=                else "",
x == 1ext if idext=raw_t,
                ocr_td.get("storage_path")th=payloaorage_pa                stme_type,
        mime_type=mie_number=idx,
                   pagriptor(
          PageDesc        = [
]

        pagesion."rom ingestge path f"Missing storareasons = [ ingestion_t"
           ion = "rejecact        next_ingestion_"
    _status = "rejected:
            ingestiontorage_path")  if not payload.get("srocess"

      on = "prepd"
        next_ingestion_acti = "accepte processing."]
        ingestion_statusetadata accepted forsons = ["File m  ingestion_reaDescriptor
      ut, Paget IngestionOutpporrom .schemas im  fion stage
      ngest        # Iation/pdf")

e", "applice_typad.get("mimme_type = paylostrip()
        mi") or "").raw_texttext = (payload.get(")
        raw_") or 1"page_countyload.get(e_count = int(pa   pag   t_id"]
  d["documen_id = payloaent"
        documI fallback)""n (same as CrewAow executiolate workfl"Simu""ate:
        rkflowStt[str, Any]) -> Wod: dicsimulate(self, payloa
    def e(payload)
    eturn self.simulat  reach stage
      ain agents for  would use LangCh # In production, this     lation logic
  
        # For now, use the simungChain"""flow using Lacessing worke document pro      """Execut-> WorkflowState:
   Any]) payload: dict[str,def execute(self,   
    ilarity."]
  rds and semantic simased on keywoClassification b" [rd",ic_keywo "semantnce, 4),, round(confidebest_type0.96)
        return or_boost, re * 0.08) + vect min(0.62 + (best_sconfidence =."]

        co classes documenttch for knownong lexical ma, ["No str "unknown"   return "unknown", 0.4,== 0:
         f best_score       i
  03
e_type else 0.amst = 0.08 if sor_boo
            vect= best_type]pe") =item.get("document_ty if  item in similar_docsorme_type = [item f saocs:
                  if similar_dost = 0.0
      vector_bof text.strip() else []
   emantic_search(text[:500], limit=3, base_filter={}) iservice.sr_search_s = vecto)

        similar_docest_type, 0.get(bscores     best_score = "unknown"
   es else get) if scor key=scores. = max(scores,      best_type text)

  rd in words if word in = sum(1 for woc_type]es[do            scorms():
in keyword_map.itec_type, words  do}
        for int] = {es: dict[str,        scor        }

", "scribble"],
en", "manualorm": ["handwritt       "handwritten_f"],
     ", "partycontract", "["agreementontract":      "c
       "shipment"],b", racking", "awing_document": ["thipp     "s,
       , "incident"]y""claim", "policnsurance_claim": [        "it"],
    applican, "emi", "ation": ["loan"n_applic    "loapassport"],
         "aadhaar", "",kyc", "government id["kyc_form":         "chant"],
    n", "mer["receipt", "txreceipt": ll"],
            "", "bie", "gst": ["invoic"invoice         {
   yword_map = }".lower()
        ke} {ocr_textame', '')get('file_n)} {payload.title', ''f"{payload.get('      text = ]

  ed by client."nt type hint provid ["Documet",n hint, 0.92, "hin        returPORTED_TYPES:
          if hint in SUPrip().lower()
  "").st_type_hint") or yload.get("document hint = (pa   ch"""
     semantic seareyword matching andssify document using k """Clat[str]]:
       loat, str, lisple[str, fext: str) -> tu Any], ocr_tpayload: dict[str,lf, y_document(se   def _classif   
     ]
             ),
    l.run(query))
self.search_tooon.dumps(=lambda query: js            func
    rical cases",ption="Search similar histo      descriledge",
          search_knowame="         n      ool(
       Tol.run(doc_type))
            ),
      icy_toson.dumps(self.poldoc_type: junc=lambda             ftype",
    ules for document t policy r="Geion      descript          kup",
ooame="policy_l          n     Tool(
        ),
                s))
 ) else pagesinstance(pages, strads(pages) if in.lon(jsocr_tool.rus: json.dumps(self.o=lambda pagenc                fu
ages",cument pCR text from doact O"Extrdescription=           ",
     ocr_tool               name="Tool(
 
              return [   
           return []
                if not Tool:
  
  ool classes"""sting tools from exiLangChain t"""Create 
        te_tools(self):ef _crea    d  )
    
          ature=0.1,
er  temp,
              I_API_KEYsettings.GEMINapi_key=          google_ ""),
      ce("gemini/",replaEMINI_MODEL.ngs.Godel=setti          mativeAI(
      tGoogleGener self.llm = ChaAPI_KEY:
           gs.GEMINI_ settinenerativeAI andtGoogleG   if Cha  archKnowledgeTool()
        self.llm = None
        
   earch_tool = Se
        self.scyLookupTool()ol = Poli.policy_toOCRTool()
        selfr_tool =     self.oct__(self):
     
    def __ini
   ow"""ing workfldocument processangChain-based    """L

class LangChainDocumentProcessor:
 
]
_form",ndwritten "contract",
    "haion",
   oan_applicat
    "ldocument","shipping_ance_claim",
    t",
    "insur "receipinvoice",
   rm",
    " "kyc_foD_TYPES = [
   one


SUPPORTEe = NystemMessagge = S
    HumanMessaool = Noneer = None
    ToldMessagesPlacehemplate = omptT   ChatPr_agent = None
  AgentExecutor = create_structured_chate
   oniveAI = N   ChatGoogleGenerattError:
 porssage
except ImMessage, SystemHumanMeimport hema     from langchain.scgchain.tools import Tool
rom lanlaceholder
    fMessagesPate, ChatPromptTemplimport ain.prompts  from langchgent
   tructured_chat_acreate_sxecutor, t AgentEn.agents impor langchaitiveAI
    fromhatGoogleGeneraai import C_gen langchain_google
try:
    fromield_extractor,
)
edgeTool,
    frchKnowlpTool,
    SeakuTool,
    PolicyLooools import (
    OCRt_ts.documenwState,
)
from .tooltput,
    WorkfloalidationOutionCheck,
    Valida,
    Vput  RoutingOuteprocessingOutput,
  
    FieldExtraction,
    Prut,ctionOutpxtra
    Eut,ClassificationOutput,
      AuditOutpt (
  chemas impor .sROMPT,
)
from
    VALIDATION_PMPT, SYSTEM_PRONG_PROMPT,
   ,
    ROUTIN_PROMPTEXTRACTIO   _PROMPT,
 SIFICATION
    CLAS_PROMPT,   AUDITimport (
 .library romptservice

from .ph_simport vector_searcearch vices.vector_sfrom serdjango.conf import settings


from 
ing import Anyfrom typt json
pornotations

ime__ import an __futurrom"
fs
""s and chainion with LangChain agentmplementatces CrewAI i Workflow
Replat Processingd Documen-base"""
LangChain